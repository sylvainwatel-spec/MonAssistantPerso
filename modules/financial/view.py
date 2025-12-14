import customtkinter as ctk

class FinancialAnalysisFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.build_ui()

from .service import FinancialService
from tkinter import simpledialog, messagebox
import threading

class FinancialAnalysisFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.service = FinancialService(app.data_manager)
        
        # Tracked stocks (loaded from settings or local storage)
        self.tracked_stocks = self.app.data_manager.get_settings().get("tracked_stocks", ["AAPL", "GOOGL", "MSFT"]) 
        self.current_stock_data = {}

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
        
        title = ctk.CTkLabel(header, text="💰 Analyse Financière", font=("Arial", 20, "bold"))
        title.pack(side="left", padx=20)

        # Main Layout
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1) # Stock List
        content.grid_columnconfigure(1, weight=3) # Detail View

        # --- LEFT: Stock List ---
        list_panel = ctk.CTkFrame(content, width=200)
        list_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(list_panel, text="Mes Actions", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.scroll_stocks = ctk.CTkScrollableFrame(list_panel, fg_color="transparent")
        self.scroll_stocks.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.update_stock_list_ui()
        
        btn_add = ctk.CTkButton(list_panel, text="+ Ajouter Action", command=self.add_stock)
        btn_add.pack(pady=10, padx=10, fill="x")

        # --- RIGHT: Detail View ---
        self.detail_panel = ctk.CTkFrame(content)
        self.detail_panel.grid(row=0, column=1, sticky="nsew")
        
        self.lbl_stock_title = ctk.CTkLabel(self.detail_panel, text="Sélectionnez une action", font=("Arial", 24, "bold"))
        self.lbl_stock_title.pack(pady=(40, 10))
        
        self.lbl_price = ctk.CTkLabel(self.detail_panel, text="--", font=("Arial", 32))
        self.lbl_price.pack(pady=10)
        
        self.lbl_change = ctk.CTkLabel(self.detail_panel, text="", font=("Arial", 16))
        self.lbl_change.pack(pady=5)
        
        self.txt_analysis = ctk.CTkTextbox(self.detail_panel, font=("Arial", 12), wrap="word")
        self.txt_analysis.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.btn_advice = ctk.CTkButton(
            self.detail_panel, 
            text="🧠 Obtenir Conseil IA", 
            fg_color="#8E24AA", 
            hover_color="#7B1FA2",
            state="disabled",
            command=self.get_ai_advice
        )
        self.btn_advice.pack(pady=20)

    def update_stock_list_ui(self):
        for widget in self.scroll_stocks.winfo_children():
            widget.destroy()
            
        for symbol in self.tracked_stocks:
            btn = ctk.CTkButton(
                self.scroll_stocks,
                text=symbol,
                fg_color="transparent",
                border_width=1,
                border_color="gray",
                text_color=("black", "white"),
                command=lambda s=symbol: self.load_stock_details(s)
            )
            btn.pack(fill="x", pady=2)
            
            # Remove button context menu or separate small button? simpler for now: just list
            
    def add_stock(self):
        symbol = simpledialog.askstring("Ajouter Action", "Entrez le symbole (ex: AAPL) :")
        if symbol:
            symbol = symbol.upper()
            if symbol not in self.tracked_stocks:
                self.tracked_stocks.append(symbol)
                self.save_stocks()
                self.update_stock_list_ui()

    def save_stocks(self):
        settings = self.app.data_manager.get_settings()
        settings["tracked_stocks"] = self.tracked_stocks
        # Note: Ideally simpler save method exists, but re-saving full config works
        self.app.data_manager.save_configuration(
            chat_provider=settings.get("chat_provider"),
            scrapegraph_provider=settings.get("scrapegraph_provider"),
            api_keys=settings.get("api_keys"), 
            endpoints=settings.get("endpoints"),
            scraping_solution=settings.get("scraping_solution"),
            visible_mode=settings.get("visible_mode"),
            scraping_browser=settings.get("scraping_browser"),
            image_gen_provider=settings.get("image_gen_provider"),
            doc_analyst_provider=settings.get("doc_analyst_provider")
        )

    def load_stock_details(self, symbol):
        self.selected_symbol = symbol
        self.lbl_stock_title.configure(text=f"Chargement {symbol}...")
        self.btn_advice.configure(state="disabled")
        self.txt_analysis.delete("0.0", "end")
        
        thread = threading.Thread(target=self._fetch_stock_data, args=(symbol,))
        thread.daemon = True
        thread.start()

    def _fetch_stock_data(self, symbol):
        success, quote, msg = self.service.get_stock_price(symbol)
        self.after(0, lambda: self._display_data(success, quote, msg, symbol))

    def _display_data(self, success, quote, msg, symbol):
        if success:
            price = quote.get("05. price")
            change = quote.get("10. change percent")
            
            self.lbl_stock_title.configure(text=f"{symbol}")
            self.lbl_price.configure(text=f"${float(price):.2f}")
            
            color = "green" if not change.startswith("-") else "red"
            self.lbl_change.configure(text=f"{change}", text_color=color)
            
            self.current_stock_data = quote
            self.btn_advice.configure(state="normal")
        else:
            self.lbl_stock_title.configure(text=f"Erreur {symbol}")
            self.lbl_price.configure(text="--")
            self.lbl_change.configure(text=msg, text_color="red")

    def get_ai_advice(self):
        if not self.selected_symbol: return
        
        self.btn_advice.configure(state="disabled", text="Analyse en cours...")
        self.txt_analysis.insert("end", "🤖 L'IA analyse les données...\n")
        
        thread = threading.Thread(target=self._fetch_advice)
        thread.daemon = True
        thread.start()
        
    def _fetch_advice(self):
        # Prepare context for LLM
        context = f"""
        Action: {self.selected_symbol}
        Prix actuel: {self.current_stock_data.get("05. price")}
        Variation: {self.current_stock_data.get("10. change percent")}
        Volume: {self.current_stock_data.get("06. volume")}
        Haut jour: {self.current_stock_data.get("03. high")}
        Bas jour: {self.current_stock_data.get("04. low")}
        
        Agis comme un expert financier. Analyse ces données techniques de base et donne un conseil court (Acheter/Vendre/Conserver) avec 3 arguments clés.
        """
        
        # Use Chat Logic (via generic connector if possible, or simple request)
        # For simplicity, using one of the configured providers from settings manually or via app's llm service if strictly exposed.
        # BUT, the prompt said "me conseiller". I'll use the LLMService instance from app if available, or create one.
        # Home page uses self.app.show_chat which uses ChatFrame which uses LLMService.
        # I'll instantiate LLMService here or reuse logic.
        
        from core.services.llm_service import LLMService
        llm_service = LLMService(self.app.data_manager)
        provider = self.app.data_manager.get_settings().get("chat_provider", "OpenAI GPT-4o mini")
        
        response = llm_service.generate_response(context, [], provider, None) # No image
        
        self.after(0, lambda: self._display_advice(response))
        
    def _display_advice(self, response):
        self.txt_analysis.delete("0.0", "end")
        self.txt_analysis.insert("end", response)
        self.btn_advice.configure(state="normal", text="🧠 Obtenir Conseil IA")
