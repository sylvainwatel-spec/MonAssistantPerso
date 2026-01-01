
import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from PIL import Image
import threading

# Import service (assuming it's in the same module structure)
# We need to make sure modules path is correct in sys.path which is done in main.py
from modules.data_viz.services import DataAnalysisService

class DataVizFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        
        # Initialize Service
        # app.data_manager should be available based on main.py App class
        if hasattr(app, 'data_manager'):
            self.service = DataAnalysisService(app.data_manager)
        else:
            # Fallback (mostly for testing isolation if needed)
            from utils.data_manager import DataManager
            self.service = DataAnalysisService(DataManager())

        self.analysis_result_text = ""
        self.build_ui()

    def build_ui(self):
        # Header
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
        
        title = ctk.CTkLabel(header, text="📈 Data Visualization", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=20)

        # Main Layout: Left Panel (Controls), Right Panel (Display)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left Panel
        left_panel = ctk.CTkFrame(main_container, width=250, corner_radius=10)
        left_panel.pack(side="left", fill="y", padx=(0, 10))

        # Controls in Left Panel
        ctk.CTkLabel(left_panel, text="Actions", font=("Arial", 16, "bold")).pack(pady=10)

        self.btn_import = ctk.CTkButton(left_panel, text="📥 Importer Fichier", command=self.import_file)
        self.btn_import.pack(pady=10, padx=20, fill="x")

        # LLM Selection
        ctk.CTkLabel(left_panel, text="Modèle IA", font=("Arial", 12)).pack(pady=(10, 0))
        self.available_providers = [
            "IAKA (Interne)",
            "OpenAI GPT-4o mini", 
            "Google Gemini 1.5 Flash", 
            "Google Gemini 2.5 Flash-Lite", 
            "Anthropic Claude Opus 4.5", 
            "Meta Llama 3 (via Groq)", 
            "Mistral NeMo", 
            "DeepSeek-V3", 
            "DeepSeek-VL", 
            "Hugging Face (Mistral/Mixtral)"
        ]
        self.cmb_provider = ctk.CTkOptionMenu(left_panel, values=self.available_providers)
        self.cmb_provider.pack(pady=(5, 10), padx=20, fill="x")
        self.cmb_provider.set("Meta Llama 3 (via Groq)")

        self.btn_analyze = ctk.CTkButton(left_panel, text="🤖 Analyser (IA)", command=self.run_analysis, state="disabled")
        self.btn_analyze.pack(pady=10, padx=20, fill="x")

        self.btn_agent = ctk.CTkButton(left_panel, text="🧠 Agent Expert (Beta)", command=self.open_agent_dialog, state="disabled", fg_color="#673AB7", hover_color="#512DA8")
        self.btn_agent.pack(pady=10, padx=20, fill="x")

        self.btn_export = ctk.CTkButton(left_panel, text="📤 Exporter PPTX", command=self.export_pptx, state="disabled")
        self.btn_export.pack(pady=10, padx=20, fill="x")

        self.lbl_status = ctk.CTkLabel(left_panel, text="Prêt", text_color="gray")
        self.lbl_status.pack(side="bottom", pady=20)

        # Right Panel (Scrollable)
        right_panel = ctk.CTkScrollableFrame(main_container, corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True)

        # Stats Area
        ctk.CTkLabel(right_panel, text="Aperçu des Données", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        self.txt_stats = ctk.CTkTextbox(right_panel, height=200)
        self.txt_stats.pack(fill="x", pady=(0, 20))
        
        # LLM Analysis Area
        ctk.CTkLabel(right_panel, text="Analyse Intelligente", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        self.txt_llm = ctk.CTkTextbox(right_panel, height=150)
        self.txt_llm.pack(fill="x", pady=(0, 20))

        # Chart Area
        ctk.CTkLabel(right_panel, text="Visualisation", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        self.chart_frame = ctk.CTkFrame(right_panel, fg_color="transparent", height=300)
        self.chart_frame.pack(fill="x", expand=True)
        self.lbl_chart = ctk.CTkLabel(self.chart_frame, text="Le graphique apparaîtra ici")
        self.lbl_chart.place(relx=0.5, rely=0.5, anchor="center")

    def import_file(self):
        file_path = filedialog.askopenfilename(
            title="Ouvrir un fichier",
            filetypes=[
                ("Excel Files", "*.xlsx *.xls"), 
                ("CSV Files", "*.csv"),
                ("Word Files", "*.docx"),
                ("PDF Files", "*.pdf"),
                ("PowerPoint Files", "*.pptx")
            ]
        )
        
        if file_path:
            self.lbl_status.configure(text="Chargement...")
            self.update_idletasks()
            
            success = self.service.load_file(file_path)
            if success:
                stats = self.service.get_basic_stats()
                self.txt_stats.delete("0.0", "end")
                self.txt_stats.insert("0.0", stats)
                
                # Enable buttons
                self.btn_analyze.configure(state="normal")
                self.btn_agent.configure(state="normal")
                self.btn_export.configure(state="normal")
                self.lbl_status.configure(text="Fichier chargé")
                
                # Auto generate chart
                self._show_chart()
            else:
                messagebox.showerror("Erreur", "Impossible de charger le fichier")
                self.lbl_status.configure(text="Erreur chargement")

    def _show_chart(self):
        fig = self.service.generate_chart()
        if fig:
            # Convert to image for CTk
            import io
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            img = Image.open(buf)
            
            # Resize if needed to fit
            # img.thumbnail((500, 300)) 
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(500, 350))
            
            self.lbl_chart.configure(image=ctk_img, text="")
            self.lbl_chart.image = ctk_img # keep ref
            
            import matplotlib.pyplot as plt
            plt.close(fig)
        else:
            self.lbl_chart.configure(image=None, text="Pas de données numériques trouvées pour le graphique.")

    def run_analysis(self):
        self.lbl_status.configure(text="Analyse en cours...")
        self.btn_analyze.configure(state="disabled")
        
        def _target():
            selected_provider = self.cmb_provider.get()
            result = self.service.analyze_with_llm(provider_override=selected_provider)
            self.analysis_result_text = result
            
            def _update():
                self.txt_llm.delete("0.0", "end")
                self.txt_llm.insert("0.0", result)
                self.lbl_status.configure(text="Analyse terminée")
                self.btn_analyze.configure(state="normal")
            
            self.after(0, _update)

        threading.Thread(target=_target).start()

    def export_pptx(self):
        default_name = f"Analyse_{self.service.current_filename}.pptx"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pptx",
            initialfile=default_name,
            filetypes=[("PowerPoint", "*.pptx")]
        )
        
        if file_path:
            self.lbl_status.configure(text="Exportation...")
            self.update_idletasks()
            
            success = self.service.export_to_pptx(file_path, self.analysis_result_text)
            
            if success:
                messagebox.showinfo("Succès", f"Fichier exporté avec succès:\n{file_path}")
                self.lbl_status.configure(text="Export terminé")
            else:
                messagebox.showerror("Erreur", "Échec de l'exportation")
                self.lbl_status.configure(text="Erreur export")

    def open_agent_dialog(self):
        """Ouvre une boite de dialogue pour poser une question à l'agent."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agent Data Expert")
        dialog.geometry("600x500")
        
        # Force top level
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Posez votre question sur les données :", font=("Arial", 14, "bold")).pack(pady=10, padx=20, anchor="w")
        
        txt_query = ctk.CTkTextbox(dialog, height=60)
        txt_query.pack(fill="x", padx=20, pady=(0, 10))
        
        btn_generate = ctk.CTkButton(dialog, text="Générer le Code", command=lambda: _generate())
        btn_generate.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Code Python proposé (Editable) :", font=("Arial", 12)).pack(pady=(15, 5), padx=20, anchor="w")
        txt_code = ctk.CTkTextbox(dialog, height=150, font=("Consolas", 12))
        txt_code.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        lbl_info = ctk.CTkLabel(dialog, text="⚠️ Vérifiez le code avant d'exécuter !", text_color="orange")
        lbl_info.pack(pady=5)
        
        btn_run = ctk.CTkButton(dialog, text="▶️ Exécuter", fg_color="green", hover_color="darkgreen", state="disabled")
        btn_run.pack(pady=10, fill="x", padx=50)
        
        def _generate():
            query = txt_query.get("0.0", "end").strip()
            if not query:
                return
            
            btn_generate.configure(state="disabled", text="Génération...")
            lbl_info.configure(text="Réflexion en cours...", text_color="gray")
            dialog.update()
            
            provider = self.cmb_provider.get()
            
            def _thread_gen():
                code, error = self.service.generate_code_from_query(query, provider_override=provider)
                
                def _ui_update():
                    btn_generate.configure(state="normal", text="Générer le Code")
                    if error:
                        messagebox.showerror("Erreur IA", error)
                        lbl_info.configure(text="Erreur lors de la génération", text_color="red")
                    else:
                        txt_code.delete("0.0", "end")
                        txt_code.insert("0.0", code)
                        btn_run.configure(state="normal", command=lambda: _execute(code)) # Bind to generated code? Better to get from text box
                        btn_run.configure(command=lambda: _execute())
                        lbl_info.configure(text="Code généré. Cliquez sur Exécuter pour lancer.", text_color="green")
                        
                self.after(0, _ui_update)
            
            threading.Thread(target=_thread_gen).start()
            
        def _execute(code_override=None):
            # Get code from textbox to allow edits
            final_code = txt_code.get("0.0", "end").strip()
            if not final_code:
                return

            btn_run.configure(state="disabled", text="Exécution...")
            dialog.update()
            
            output, fig = self.service.execute_generated_code(final_code)
            
            # Show results in main window
            self.txt_llm.delete("0.0", "end")
            self.txt_llm.insert("0.0", f"--- Résultat Agent ---\n\n{output}")
            
            if fig:
                # Same logic as show_chart
                import io
                buf = io.BytesIO()
                fig.savefig(buf, format='png')
                buf.seek(0)
                img = Image.open(buf)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(500, 350))
                self.lbl_chart.configure(image=ctk_img, text="")
                self.lbl_chart.image = ctk_img
                import matplotlib.pyplot as plt
                plt.close(fig)
            
            dialog.destroy()
            self.lbl_status.configure(text="Action Agent terminée")
