import customtkinter as ctk
import os
from PIL import Image
from utils.resource_handler import resource_path

class ToolTip:
    """Class to create tooltips on hover."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.after_id = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2 - 30
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        
        if self.tooltip is None:
            self.tooltip = ctk.CTkToplevel(self.widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            self.tooltip.attributes("-topmost", True) # Ensure on top
            
            label = ctk.CTkLabel(
                self.tooltip,
                text=self.text,
                font=("Arial", 11),
                fg_color=("gray90", "gray20"),
                text_color=("black", "white"),
                corner_radius=6,
                padx=8,
                pady=4
            )
            label.pack()
            
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class FeatureCard(ctk.CTkFrame):
    def __init__(self, master, title, description, icon_text, color, command):
        # Slightly different background for card contrast
        super().__init__(master, fg_color=("white", "gray17"), corner_radius=20, border_width=0)
        
        self.command = command
        self.default_fg = ("white", "gray17")
        self.hover_fg = ("gray95", "gray22")
        
        # Event bindings for hover and click
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", lambda e: self.command())
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Icon
        self.grid_rowconfigure(1, weight=0) # Title
        self.grid_rowconfigure(2, weight=1) # Description
        self.grid_rowconfigure(3, weight=0) # Action hint
        
        # 1. Icon Header
        self.lbl_icon = ctk.CTkLabel(
            self, 
            text=icon_text, 
            font=("Segoe UI Emoji", 42), # Standard Windows Emoji font
            text_color=color
        )
        self.lbl_icon.grid(row=0, column=0, pady=(25, 10))
        self.lbl_icon.bind("<Button-1>", lambda e: self.command())
        self.lbl_icon.bind("<Enter>", self.on_enter)
        self.lbl_icon.bind("<Leave>", self.on_leave)

        # 2. Title
        self.lbl_title = ctk.CTkLabel(
            self, 
            text=title, 
            font=("Arial", 18, "bold"),
            text_color=("gray15", "gray90")
        )
        self.lbl_title.grid(row=1, column=0, padx=15)
        self.lbl_title.bind("<Button-1>", lambda e: self.command())
        self.lbl_title.bind("<Enter>", self.on_enter)
        self.lbl_title.bind("<Leave>", self.on_leave)
        
        # 3. Description
        self.lbl_desc = ctk.CTkLabel(
            self, 
            text=description, 
            font=("Arial", 12),
            text_color=("gray50", "gray60"),
            wraplength=200,
            justify="center"
        )
        self.lbl_desc.grid(row=2, column=0, padx=20, pady=(5, 10))
        self.lbl_desc.bind("<Button-1>", lambda e: self.command())
        self.lbl_desc.bind("<Enter>", self.on_enter)
        self.lbl_desc.bind("<Leave>", self.on_leave)
        
        # 4. Action Hint (Arrow)
        self.lbl_action = ctk.CTkLabel(
            self,
            text="Ouvrir →",
            font=("Arial", 11, "bold"),
            text_color=color
        )
        self.lbl_action.grid(row=3, column=0, pady=(0, 20))
        self.lbl_action.bind("<Button-1>", lambda e: self.command())
        self.lbl_action.bind("<Enter>", self.on_enter)
        self.lbl_action.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(fg_color=self.hover_fg)
        
    def on_leave(self, event):
        self.configure(fg_color=self.default_fg)


class HomeFrame(ctk.CTkFrame):

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        
        # --- Top Bar ---
        # Configure grid for the home page
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Content
        
        # Header Frame (Row 0)
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 0))

        # Explicit Background Setup for HomeFrame
        try:
            bg_path = resource_path(os.path.join("image", "Page_accueil.png"))
            if os.path.exists(bg_path):
                pil_img = Image.open(bg_path)
                # Ensure the image covers the frame. Size might need adjustment or dynamic resizing.
                # using a large fixed size for now or matching app size roughly.
                self.bg_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(1100, 850)) 
                self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_image)
                self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
                self.bg_label.lower() # Send to back
                print("DEBUG: HomeFrame background set explicitly.")
        except Exception as e:
            print(f"DEBUG: HomeFrame background error: {e}")


        # Admin Button (Right aligned in Header)
        btn_admin = ctk.CTkButton(
            self.header_frame,
            text="⚙️",
            width=45,
            height=45,
            font=("Segoe UI Emoji", 20),
            fg_color=("white", "gray17"),
            hover_color=("gray90", "gray25"),
            text_color="gray",
            corner_radius=15,
            command=self.app.show_admin
        )
        btn_admin.pack(side="right")

        # (Background logic moved to end of __init__)
        
        # --- Container for Content ---
        # Changed to CTkScrollableFrame to allow vertical scrolling
        self.content_scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent", 
            width=800
        )
        self.content_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_scroll.grid_columnconfigure(0, weight=1)
        
        # Hero Section (Centered)
        self.hero_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.hero_frame.pack(pady=(20, 20))
        
        # (Avatar removed from here)
        
        # Welcome Text
        welcome_lbl = ctk.CTkLabel(
            self.hero_frame, 
            text="Bienvenue",
            font=("Helvetica", 32, "bold"),
            text_color=("gray20", "gray95")
        )
        welcome_lbl.pack()
        
        subtitle_lbl = ctk.CTkLabel(
            self.hero_frame,
            text="Votre espace de travail IA personnel",
            font=("Helvetica", 16),
            text_color=("gray50", "gray60")
        )
        subtitle_lbl.pack(pady=(5, 0))

        # --- Cards Grid ---
        self.cards_container = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.cards_container.pack(fill="x", padx=20, pady=20)
        self.cards_container.grid_columnconfigure(0, weight=1)
        self.cards_container.grid_columnconfigure(1, weight=1)
        self.cards_container.grid_columnconfigure(2, weight=1)
        
        # Card 1: Assistants
        self.card_1 = FeatureCard(
            self.cards_container,
            title="Mes Assistants",
            description="Créez, gérez et discutez avec vos assistants virtuels intelligents.",
            icon_text="💬",
            color="#2196F3",
            command=self.app.show_list
        )
        self.card_1.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Card 2: Image Studio
        self.card_2 = FeatureCard(
            self.cards_container,
            title="Studio Image",
            description="Donnez vie à vos idées avec des outils de génération d'image avancés.",
            icon_text="🎨",
            color="#E91E63", 
            command=self.app.show_image_gen
        )
        self.card_2.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        
        # Card 3: Doc Analyst
        self.card_3 = FeatureCard(
            self.cards_container,
            title="Analyse Docs",
            description="Analysez vos documents PDF et extrayez des informations clés.",
            icon_text="📄",
            color="#4CAF50",
            command=self.app.show_doc_analyst
        )
        self.card_3.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")

        # Card 4: Data Visualization
        self.card_4 = FeatureCard(
            self.cards_container,
            title="Data Viz",
            description="Créez des graphiques interactifs à partir de vos données.",
            icon_text="📈",
            color="#FF9800",
            command=self.app.show_data_viz
        )
        self.card_4.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        # Card 5: Financial Analysis
        self.card_5 = FeatureCard(
            self.cards_container,
            title="Finance",
            description="Analysez des données financières et de marché.",
            icon_text="💰",
            color="#9C27B0",
            command=self.app.show_financial
        )
        self.card_5.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")

        # Card 6: Scraping Tool
        self.card_6 = FeatureCard(
            self.cards_container,
            title="Scraping",
            description="Extractez des données depuis n'importe quelle URL.",
            icon_text="🕸️",
            color="#FF5722",
            command=self.app.show_scraping
        )
        self.card_6.grid(row=1, column=2, padx=15, pady=15, sticky="nsew")


