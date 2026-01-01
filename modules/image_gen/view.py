import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from PIL import Image
from .service import ImageGenerationService

class ImageGenFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.service = ImageGenerationService(app.data_manager)
        
        # Generated image storage
        self.current_image = None
        self.imported_image_path = None # For Img2Img
        self.imported_image_path_2 = None # For Qwen Dual Image
        
        self.max_image_display_size = (512, 512)

        # Build UI
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
        
        title = ctk.CTkLabel(header, text="🎨 Studio Image", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=20)

        # 2. Main Content (Split 50/50)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1) # Left: Controls
        content.grid_columnconfigure(1, weight=1) # Right: Preview
        content.grid_rowconfigure(0, weight=1)

        # --- Left Panel: Controls ---
        left_panel = ctk.CTkFrame(content)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # --- Import Image Section ---
        ctk.CTkLabel(left_panel, text="Image Source (Optionnel)", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        
        btn_import = ctk.CTkButton(
            left_panel,
            text="📂 Importer une image",
            height=30,
            fg_color="gray40",
            hover_color="gray50",
            command=self.import_image
        )
        btn_import.pack(fill="x", padx=20, pady=(0, 5))
        
        self.lbl_imported_info = ctk.CTkLabel(left_panel, text="Aucune image importée", font=("Arial", 11), text_color="gray")
        self.lbl_imported_info.pack(anchor="w", padx=20, pady=(0, 10))
        
        self.btn_clear_import = ctk.CTkButton(
            left_panel,
            text="❌ Supprimer",
            height=20,
            width=80,
            fg_color="transparent",
            text_color="red",
            hover_color=("gray90", "gray20"),
            command=self.clear_imported_image
        )
        self.btn_clear_import.pack(anchor="e", padx=20, pady=(0, 10))
        self.btn_clear_import.pack_forget()

        # --- Import Image Section 2 (Optional) ---
        ctk.CTkLabel(left_panel, text="Image Source 2 (Optionnel, pour Qwen)", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        btn_import_2 = ctk.CTkButton(
            left_panel,
            text="📂 Importer image 2",
            height=30,
            fg_color="gray40",
            hover_color="gray50",
            command=self.import_image_2
        )
        btn_import_2.pack(fill="x", padx=20, pady=(0, 5))
        
        self.lbl_imported_info_2 = ctk.CTkLabel(left_panel, text="Aucune image importée", font=("Arial", 11), text_color="gray")
        self.lbl_imported_info_2.pack(anchor="w", padx=20, pady=(0, 10))
        
        self.btn_clear_import_2 = ctk.CTkButton(
            left_panel,
            text="❌ Supprimer",
            height=20,
            width=80,
            fg_color="transparent",
            text_color="red",
            hover_color=("gray90", "gray20"),
            command=self.clear_imported_image_2
        )
        self.btn_clear_import_2.pack(anchor="e", padx=20, pady=(0, 10))
        self.btn_clear_import_2.pack_forget()

        # --- Prompt Section ---
        ctk.CTkLabel(left_panel, text="Votre Prompt", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.txt_prompt = ctk.CTkTextbox(left_panel, height=150, font=("Arial", 12))
        self.txt_prompt.pack(fill="x", padx=20, pady=(0, 20))
        self.txt_prompt.insert("1.0", "Un astronaute chevauchant un cheval sur Mars, style photoréaliste, 4k")

        # Options
        ctk.CTkLabel(left_panel, text="Options", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(0, 5))
        
        settings = self.app.data_manager.get_settings()
        default_provider = settings.get("image_gen_provider", "OpenAI DALL-E 3")
        self.var_provider = ctk.StringVar(value=default_provider)
        combo_provider = ctk.CTkOptionMenu(
            left_panel, 
            variable=self.var_provider, 
            values=[
                "OpenAI DALL-E 3", 
                "OpenAI DALL-E 2", 
                "Stable Diffusion XL", 
                "FLUX.1 [schnell]", 
                "Stable Diffusion 3.5 Large",
                "Qwen-Image-Edit-2509"
            ]
        )
        combo_provider.pack(fill="x", padx=20, pady=(0, 10))
        
        self.var_size = ctk.StringVar(value="8x8")
        combo_size = ctk.CTkOptionMenu(
            left_panel, 
            variable=self.var_size, 
            values=["1024x1024", "512x512", "256x256", "64x64", "32x32", "16x16", "8x8"]
        )
        combo_size.pack(fill="x", padx=20, pady=(0, 20))
        
        # Generate Button
        self.btn_generate = ctk.CTkButton(
            left_panel,
            text="✨ Générer l'image",
            height=50,
            font=("Arial", 16, "bold"),
            fg_color="#E91E63", # Pink/Purple
            hover_color="#C2185B",
            command=self.start_generation
        )
        self.btn_generate.pack(fill="x", padx=20, pady=(10, 20))
        
        # Progress Bar
        self.progress = ctk.CTkProgressBar(
            left_panel, 
            mode="indeterminate",
            height=8,
            corner_radius=4,
            progress_color=("#4CAF50", "#4CAF50"),
            fg_color=("gray85", "gray25")
        )
        self.progress.pack(fill="x", padx=20, pady=(0, 20))
        self.progress.pack_forget() # Hide initially

        # --- Right Panel: Preview ---
        right_panel = ctk.CTkFrame(content, fg_color=("gray90", "gray15"))
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        self.lbl_preview = ctk.CTkLabel(right_panel, text="L'image générée apparaîtra ici")
        self.lbl_preview.place(relx=0.5, rely=0.5, anchor="center")
        
        self.btn_save = ctk.CTkButton(
            right_panel,
            text="💾 Enregistrer",
            state="disabled",
            command=self.save_image
        )
        self.btn_save.pack(side="bottom", pady=20)

    def start_generation(self):
        prompt = self.txt_prompt.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showwarning("Attention", "Veuillez entrer une description pour l'image.")
            return

        self.btn_generate.configure(state="disabled", text="Génération en cours...")
        self.progress.pack(fill="x", padx=20, pady=(0, 20), before=self.btn_generate)
        self.progress.start()
        
        
        # Threaded call
        thread = threading.Thread(target=self._generate_thread, args=(prompt, self.imported_image_path, self.imported_image_path_2))
        thread.daemon = True
        thread.start()

    def _generate_thread(self, prompt, image_path=None, image_path_2=None):
        provider = self.var_provider.get()
        size = self.var_size.get()
        
        success, image, message = self.service.generate_image(prompt, provider, size, image_path, image_path_2)
        
        # Update UI in main thread using after (safe for Tkinter)
        self.after(0, lambda: self._on_generation_complete(success, image, message))

    def _on_generation_complete(self, success, image, message):
        self.progress.stop()
        self.progress.pack_forget()
        self.btn_generate.configure(state="normal", text="✨ Générer l'image")
        
        if success and image:
            self.current_image = image
            
            # Resize for display
            display_img = image.copy()
            display_img.thumbnail(self.max_image_display_size, Image.Resampling.LANCZOS)
            
            ctk_img = ctk.CTkImage(light_image=display_img, dark_image=display_img, size=display_img.size)
            
            self.lbl_preview.configure(image=ctk_img, text="")
            self.btn_save.configure(state="normal")
        else:
            messagebox.showerror("Erreur", message)

    def save_image(self):
        if not self.current_image:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Enregistrer l'image"
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                messagebox.showinfo("Succès", "Image enregistrée !")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'enregistrer : {e}")

    def import_image(self):
        file_path = filedialog.askopenfilename(
            title="Importer une image source",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")]
        )
        if file_path:
            self.imported_image_path = file_path
            filename = file_path.split("/")[-1]
            self.lbl_imported_info.configure(text=f"Image : {filename}", text_color=("black", "white"))
            self.btn_clear_import.pack(anchor="e", padx=20, pady=(0, 10))
            
            # Show preview if possible? (Simulated by label update for now)
            # We could do a small thumbnail, but let's keep it simple.

    def clear_imported_image(self):
        self.imported_image_path = None
        self.lbl_imported_info.configure(text="Aucune image importée", text_color="gray")
        self.btn_clear_import.pack_forget()

    def import_image_2(self):
        file_path = filedialog.askopenfilename(
            title="Importer une image source 2",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")]
        )
        if file_path:
            self.imported_image_path_2 = file_path
            filename = file_path.split("/")[-1]
            self.lbl_imported_info_2.configure(text=f"Image : {filename}", text_color=("black", "white"))
            self.btn_clear_import_2.pack(anchor="e", padx=20, pady=(0, 10))

    def clear_imported_image_2(self):
        self.imported_image_path_2 = None
        self.lbl_imported_info_2.configure(text="Aucune image importée", text_color="gray")
        self.btn_clear_import_2.pack_forget()
