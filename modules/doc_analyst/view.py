import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
try:
    from docx import Document
except ImportError:
    Document = None
from .service import DocumentAnalysisService

class DocAnalystFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.service = DocumentAnalysisService(app.data_manager)
        
        self.current_document_text = ""
        self.chat_history = [] # List of {"role": "...", "content": "..."}

        self.build_ui()

    def build_ui(self):
        # 1. Header
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.pack(fill="x", padx=20, pady=10)
        
        btn_back = ctk.CTkButton(
            header,
            text="< Accueil",
            width=100,
            height=32,
            fg_color=("gray70", "gray30"),
            corner_radius=16,
            command=self.app.show_home,
        )
        btn_back.pack(side="left", padx=10, pady=10)
        
        title = ctk.CTkLabel(header, text="📄 Analyse de Documents (Beta)", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=20)

        # 2. Main Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.grid_columnconfigure(0, weight=3) # Chat area
        content.grid_columnconfigure(1, weight=1) # Controls
        content.grid_rowconfigure(0, weight=1)

        # --- Left: Chat Area ---
        chat_panel = ctk.CTkFrame(content)
        chat_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        chat_panel.grid_rowconfigure(0, weight=1)
        chat_panel.grid_columnconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(chat_panel, state="disabled", font=("Arial", 12))
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        input_frame = ctk.CTkFrame(chat_panel, height=50)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        self.msg_entry = ctk.CTkEntry(input_frame, placeholder_text="Posez votre question sur le document...")
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message)
        
        self.btn_send = ctk.CTkButton(input_frame, text="Envoyer", width=100, command=self.send_message)
        self.btn_send.pack(side="right")
        
        # Loading Indicator (Progress Bar Style)
        self.progress_bar = ctk.CTkProgressBar(
            chat_panel,
            mode="indeterminate",
            height=8,
            corner_radius=4,
            progress_color=("#4CAF50", "#4CAF50"),
            fg_color=("gray85", "gray25")
        )
        # Initially hidden
        self.progress_bar.set(0)

        # --- Right: Controls ---
        controls_panel = ctk.CTkFrame(content, width=250)
        controls_panel.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(controls_panel, text="Document", font=("Arial", 14, "bold")).pack(pady=20)
        
        self.btn_upload = ctk.CTkButton(
            controls_panel, 
            text="📂 Charger PDF / TXT",
            command=self.upload_document
        )
        self.btn_upload.pack(pady=10, padx=20, fill="x")
        
        
        self.lbl_filename = ctk.CTkLabel(controls_panel, text="Aucun fichier chargé", text_color="gray")
        self.lbl_filename.pack(pady=5)
        
        ctk.CTkLabel(controls_panel, text="Paramètres", font=("Arial", 14, "bold")).pack(pady=(30, 10))
        
        # Provider Selection
        self.var_provider = ctk.StringVar(value="")
        self.combo_provider = ctk.CTkOptionMenu(controls_panel, variable=self.var_provider, values=[])
        self.combo_provider.pack(pady=10, padx=20, fill="x")
        self.update_provider_list()

        # Export Button at Bottom
        self.btn_export = ctk.CTkButton(
            controls_panel, 
            text="💾  Exporter l'analyse (Word)",
            font=("Arial", 14, "bold"),
            height=40,
            fg_color="#2B579A", # Professional Word Blue
            hover_color="#1E3E70",
            command=self.export_to_word
        )
        self.btn_export.pack(side="bottom", pady=20, padx=20, fill="x")

        
    def update_provider_list(self):
        # Hardcoded Hugging Face models for Document Analysis
        self.hf_models = [
            "IAKA (Interne)",
            "Qwen 2.5 72B (Hugging Face)"
        ]
        
        self.combo_provider.configure(values=self.hf_models)
        
        settings = self.app.data_manager.get_settings()
        default_provider = settings.get("doc_analyst_provider")
        
        if default_provider and default_provider in self.hf_models:
            self.var_provider.set(default_provider)
        else:
            self.var_provider.set(self.hf_models[0])

    def upload_document(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF Documents", "*.pdf"), ("Text Files", "*.txt")]
        )
        if not file_path:
            return

        success, result = self.service.extract_text(file_path)
        if success:
            self.current_document_text = result
            filename = file_path.split("/")[-1]
            self.lbl_filename.configure(text=f"✅ {filename}\n({len(result)} caractères)")
            self.append_chat("System", f"Document '{filename}' chargé avec succès. Vous pouvez poser des questions.")
            self.chat_history = [] # Reset history
        else:
            messagebox.showerror("Erreur", result)

    def send_message(self, event=None):
        if not self.current_document_text:
            messagebox.showwarning("Info", "Veuillez d'abord charger un document.")
            return
            
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        provider = self.var_provider.get()
        if not provider or provider == "Aucun provider configuré":
            messagebox.showerror("Erreur", "Veuillez sélectionner un provider LLM.")
            return

        self.append_chat("Vous", msg)
        self.msg_entry.delete(0, "end")
        self.btn_send.configure(state="disabled")
        
        # Show loading indicator
        self.progress_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.progress_bar.start()

        # Threaded call
        thread = threading.Thread(target=self._chat_thread, args=(msg, provider))
        thread.daemon = True
        thread.start()

    def _chat_thread(self, msg, provider):
        success, response = self.service.chat_with_document(
            self.current_document_text,
            msg,
            self.chat_history,
            provider
        )
        self.after(0, lambda: self._on_response(success, response, msg))

    def _on_response(self, success, response, user_msg):
        self.progress_bar.stop()
        self.progress_bar.grid_forget() # Hide loading
        self.btn_send.configure(state="normal")
        if success:
            self.append_chat("Assistant", response)
            # Add to history
            self.chat_history.append({"role": "user", "content": user_msg})
            self.chat_history.append({"role": "assistant", "content": response})
        else:
            self.append_chat("System", f"Erreur: {response}")

    def append_chat(self, sender, text):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n[{sender}]: {text}\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def export_to_word(self):
        if not self.chat_history:
            messagebox.showinfo("Info", "Aucune conversation à exporter.")
            return

        if Document is None:
             messagebox.showerror("Erreur", "La librairie 'python-docx' n'est pas installée.")
             return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Documents", "*.docx")]
        )
        if not file_path:
            return

        try:
            doc = Document()
            # Clean filename from label text
            raw_filename = self.lbl_filename.cget("text")
            clean_filename = raw_filename.replace("✅ ", "").splitlines()[0] if "✅" in raw_filename else "Document"
            
            doc.add_heading(f"Analyse de Document : {clean_filename}", 0)

            for msg in self.chat_history:
                sender = "Utilisateur" if msg["role"] == "user" else "Assistant"
                p = doc.add_paragraph()
                p.add_run(f"[{sender}]: ").bold = True
                p.add_run(msg["content"])
                
            doc.save(file_path)
            messagebox.showinfo("Succès", "Export réussi !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export : {e}")
