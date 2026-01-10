"""
Knowledge Base Manager - Administration interface for RAG.
Allows creating, indexing, and managing knowledge bases.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from typing import Optional

from core.services.vector_store_service import VectorStoreService
from core.services.document_ingestion_service import DocumentIngestionService


class KnowledgeBaseManagerFrame(ctk.CTkFrame):
    """Frame for managing knowledge bases."""
    
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.data_manager = app.data_manager
        
        # Services (Initialized lazily)
        self.vector_store = None
        self.ingestion_service = None
        
        # Current KB being edited
        self.current_kb_id = None
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Main content (scrollable)
        self.content_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Start initialization process
        self.show_loading_view()
        self.after(100, self._initialize_services)
        
    def show_loading_view(self):
        """Show loading indicator during initialization."""
        self.loading_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.loading_container.grid(row=0, column=0, pady=100)
        
        ctk.CTkLabel(
            self.loading_container, 
            text="🚀 Chargement du moteur IA...", 
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            self.loading_container, 
            text="Le premier accès peut prendre quelques secondes\npour initialiser les composants (ChromaDB, LangChain).", 
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=5)
        
        self.loading_bar = ctk.CTkProgressBar(self.loading_container, width=300)
        self.loading_bar.pack(pady=20)
        self.loading_bar.configure(mode="indeterminate")
        self.loading_bar.start()

    def _initialize_services(self):
        """Initialize heavy services in background-like manner."""
        try:
            # Force UI update to show loader
            self.update_idletasks()
            
            # Initialize services (Triggering heavy lazy imports)
            if self.vector_store is None:
                self.vector_store = VectorStoreService()
            
            if self.ingestion_service is None:
                self.ingestion_service = DocumentIngestionService()
                
            # Clear loader and show content
            self.loading_bar.stop()
            for widget in self.content_frame.winfo_children():
                widget.destroy()
                
            self.show_list_view()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec du chargement des services IA:\n{str(e)}")
            # Optional: Allow retry or return to admin
            btn_retry = ctk.CTkButton(
                self.content_frame, 
                text="Réessayer", 
                command=self._initialize_services
            )
            btn_retry.grid(row=2, column=0, pady=20)
    
    def create_header(self):
        """Create header with back button and title."""
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        btn_back = ctk.CTkButton(
            header,
            text="< Administration",
            width=150,
            height=32,
            fg_color=("gray70", "gray30"),
            corner_radius=16,
            command=self.app.show_admin
        )
        btn_back.pack(side="left", padx=10)
        
        title = ctk.CTkLabel(
            header,
            text="📚 Bases de Connaissances",
            font=("Arial", 24, "bold")
        )
        title.pack(side="left", padx=20)
    
    def clear_content(self):
        """Clear all widgets from content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_list_view(self):
        """Show list of all knowledge bases."""
        self.clear_content()
        self.current_kb_id = None
        
        # Title and actions
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # New KB button
        btn_new = ctk.CTkButton(
            header_frame,
            text="+ Nouvelle Base",
            width=150,
            height=35,
            fg_color=("#3B8ED0", "#1F6AA5"),
            command=self.show_create_view
        )
        btn_new.grid(row=0, column=0, padx=5)
        
        # Refresh button
        btn_refresh = ctk.CTkButton(
            header_frame,
            text="🔄 Rafraîchir",
            width=120,
            height=35,
            fg_color=("gray70", "gray30"),
            command=self.show_list_view
        )
        btn_refresh.grid(row=0, column=2, padx=5)

        # Cleanup button
        btn_cleanup = ctk.CTkButton(
            header_frame,
            text="🧹 Nettoyage Disque",
            width=140,
            height=35,
            fg_color=("gray70", "gray30"),
            command=self.perform_cleanup
        )
        btn_cleanup.grid(row=0, column=3, padx=5)

        # Get all knowledge bases
        knowledge_bases = self.data_manager.get_all_knowledge_bases()
        
        if not knowledge_bases:
            # Empty state
            empty_frame = ctk.CTkFrame(
                self.content_frame,
                fg_color=("gray95", "gray20"),
                corner_radius=12
            )
            empty_frame.grid(row=1, column=0, sticky="ew", pady=20)
            
            ctk.CTkLabel(
                empty_frame,
                text="📚",
                font=("Arial", 48)
            ).pack(pady=(30, 10))
            
            ctk.CTkLabel(
                empty_frame,
                text="Aucune base de connaissances",
                font=("Arial", 18, "bold")
            ).pack()
            
            ctk.CTkLabel(
                empty_frame,
                text="Créez votre première base pour commencer à indexer vos documents",
                font=("Arial", 12),
                text_color="gray"
            ).pack(pady=(5, 30))
        else:
            # List of KBs
            for i, kb in enumerate(knowledge_bases):
                self.create_kb_card(kb, row=i+1)

    def perform_cleanup(self):
        """Perform manual cleanup of orphan files."""
        if not messagebox.askyesno("Confirmations", "Nettoyer les fichiers orphelins sur le disque ?\n\nCela supprimera les données des bases effacées qui occupent encore de l'espace."):
            return
            
        try:
            results = self.vector_store.cleanup_orphan_files()
            
            deleted_count = len(results["deleted"])
            failed_count = len(results["failed"])
            
            msg = f"Nettoyage terminé.\n\n✅ {deleted_count} dossier(s) supprimé(s)."
            
            if failed_count > 0:
                msg += f"\n\n⚠️ {failed_count} dossier(s) verrouillé(s) par Windows."
                msg += "\n\n💡 Conseil : Redémarrez l'application pour libérer les verrous, puis relancez le nettoyage."
                icon = "warning"
            else:
                icon = "info"
                
            messagebox.showinfo("Résultat", msg, icon=icon)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du nettoyage: {str(e)}")
    
    def create_kb_card(self, kb: dict, row: int):
        """Create a card for a knowledge base."""
        card = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=12
        )
        card.grid(row=row, column=0, sticky="ew", pady=10)
        card.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(card, text="🧠", font=("Arial", 32))
        icon_label.grid(row=0, column=0, rowspan=3, padx=20, pady=20)
        
        # Name
        name_label = ctk.CTkLabel(
            card,
            text=kb["name"],
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=1, sticky="w", pady=(20, 5))
        
        # Stats
        stats_text = f"{kb.get('document_count', 0)} documents • {kb.get('chunk_count', 0)} chunks"
        stats_label = ctk.CTkLabel(
            card,
            text=stats_text,
            font=("Arial", 12),
            text_color="gray",
            anchor="w"
        )
        stats_label.grid(row=1, column=1, sticky="w")
        
        # Last updated
        updated_text = f"Dernière MAJ: {kb.get('updated_at', 'N/A')[:16].replace('T', ' ')}"
        updated_label = ctk.CTkLabel(
            card,
            text=updated_text,
            font=("Arial", 10),
            text_color="gray",
            anchor="w"
        )
        updated_label.grid(row=2, column=1, sticky="w", pady=(0, 20))
        
        # Actions
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=3, padx=20, pady=20)
        
        btn_index = ctk.CTkButton(
            actions_frame,
            text="📂 Indexer",
            width=100,
            command=lambda: self.show_index_view(kb["id"])
        )
        btn_index.pack(pady=5)
        
        btn_delete = ctk.CTkButton(
            actions_frame,
            text="🗑️ Supprimer",
            width=100,
            fg_color=("#D32F2F", "#B71C1C"),
            hover_color=("#C62828", "#A51A1A"),
            command=lambda: self.delete_kb(kb["id"], kb["name"])
        )
        btn_delete.pack(pady=5)
    
    def show_create_view(self):
        """Show form to create a new knowledge base."""
        self.clear_content()
        
        # Title
        title_label = ctk.CTkLabel(
            self.content_frame,
            text="Créer une Nouvelle Base de Connaissances",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Form frame
        form_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=12
        )
        form_frame.grid(row=1, column=0, sticky="ew", pady=10)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Name
        ctk.CTkLabel(
            form_frame,
            text="Nom:",
            font=("Arial", 14)
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        self.name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Documentation Technique",
            width=400
        )
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=20, pady=(20, 10))
        
        # Description
        ctk.CTkLabel(
            form_frame,
            text="Description:",
            font=("Arial", 14)
        ).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        
        self.desc_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: Manuels et guides techniques",
            width=400
        )
        self.desc_entry.grid(row=1, column=1, sticky="ew", padx=20, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        btn_cancel = ctk.CTkButton(
            btn_frame,
            text="Annuler",
            width=120,
            fg_color=("gray70", "gray30"),
            command=self.show_list_view
        )
        btn_cancel.pack(side="left", padx=5)
        
        btn_create = ctk.CTkButton(
            btn_frame,
            text="Créer",
            width=120,
            fg_color=("#4CAF50", "#388E3C"),
            command=self.create_kb
        )
        btn_create.pack(side="left", padx=5)
    
    def create_kb(self):
        """Create a new knowledge base."""
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        
        if not name:
            messagebox.showerror("Erreur", "Le nom est obligatoire")
            return
        
        try:
            # Create in DataManager
            kb = self.data_manager.save_knowledge_base(name, description)
            
            # Create in VectorStore
            self.vector_store.create_knowledge_base(kb["id"], name, description)
            
            messagebox.showinfo("Succès", f"Base de connaissances '{name}' créée !")
            self.show_index_view(kb["id"])
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création: {str(e)}")
    
    def show_index_view(self, kb_id: str):
        """Show indexation interface for a knowledge base."""
        self.clear_content()
        self.current_kb_id = kb_id
        
        kb = self.data_manager.get_knowledge_base_by_id(kb_id)
        if not kb:
            messagebox.showerror("Erreur", "Base de connaissances introuvable")
            self.show_list_view()
            return
        
        # Back button and title
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        btn_back = ctk.CTkButton(
            header_frame,
            text="< Retour",
            width=100,
            fg_color=("gray70", "gray30"),
            command=self.show_list_view
        )
        btn_back.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"📚 {kb['name']}",
            font=("Arial", 18, "bold")
        )
        title_label.pack(side="left", padx=20)
        
        # Info frame
        info_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=12
        )
        info_frame.grid(row=1, column=0, sticky="ew", pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=kb.get("description", ""),
            font=("Arial", 12),
            text_color="gray"
        ).pack(padx=20, pady=10)
        
        # Import folder section
        folder_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=12
        )
        folder_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        ctk.CTkLabel(
            folder_frame,
            text="📂 Importer un dossier",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        btn_browse_folder = ctk.CTkButton(
            folder_frame,
            text="Parcourir...",
            width=150,
            command=self.import_folder
        )
        btn_browse_folder.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Import file section
        file_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=12
        )
        file_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        ctk.CTkLabel(
            file_frame,
            text="📄 Importer un fichier",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        btn_browse_file = ctk.CTkButton(
            file_frame,
            text="Parcourir...",
            width=150,
            command=self.import_file
        )
        btn_browse_file.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Progress frame
        self.progress_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=12
        )
        self.progress_frame.grid(row=4, column=0, sticky="ew", pady=10)
        
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Prêt à indexer",
            font=("Arial", 12)
        )
        self.progress_label.pack(padx=20, pady=(15, 5))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=400)
        self.progress_bar.pack(padx=20, pady=(0, 15))
        self.progress_bar.set(0)
        
        # Stats frame
        self.stats_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=("gray95", "gray20"),
            corner_radius=12
        )
        self.stats_frame.grid(row=5, column=0, sticky="ew", pady=10)
        
        self.update_stats_display(kb)
    
    def update_stats_display(self, kb: dict):
        """Update statistics display."""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(
            self.stats_frame,
            text="Statistiques:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        stats_text = f"• {kb.get('document_count', 0)} documents indexés\n"
        stats_text += f"• {kb.get('chunk_count', 0)} chunks créés\n"
        stats_text += f"• Dernière MAJ: {kb.get('updated_at', 'N/A')[:16].replace('T', ' ')}"
        
        ctk.CTkLabel(
            self.stats_frame,
            text=stats_text,
            font=("Arial", 12),
            text_color="gray",
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 15))
    
    def import_folder(self):
        """Import all files from a folder."""
        folder_path = filedialog.askdirectory(title="Sélectionner un dossier")
        if not folder_path:
            return
        
        # Start ingestion in background thread
        thread = threading.Thread(
            target=self._ingest_folder_thread,
            args=(folder_path,),
            daemon=True
        )
        thread.start()
    
    def import_file(self):
        """Import a single file."""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier",
            filetypes=[
                ("Documents", "*.pdf *.docx *.txt"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("Text", "*.txt"),
                ("Tous", "*.*")
            ]
        )
        if not file_path:
            return
        
        # Start ingestion in background thread
        thread = threading.Thread(
            target=self._ingest_file_thread,
            args=(file_path,),
            daemon=True
        )
        thread.start()
    
    def _ingest_folder_thread(self, folder_path: str):
        """Ingest folder in background thread."""
        def progress_callback(message: str, progress: float):
            self.progress_label.configure(text=message)
            self.progress_bar.set(progress)
        
        try:
            result = self.ingestion_service.ingest_folder(
                self.current_kb_id,
                folder_path,
                progress_callback
            )
            
            # Update stats
            kb = self.data_manager.get_knowledge_base_by_id(self.current_kb_id)
            current_doc_count = kb.get("document_count", 0) if kb else 0
            new_doc_count = current_doc_count + result["files_processed"]
            
            stats = self.vector_store.get_stats(self.current_kb_id)
            self.data_manager.update_knowledge_base(
                self.current_kb_id,
                chunk_count=stats["chunk_count"],
                document_count=new_doc_count
            )
            
            # Refresh display
            kb = self.data_manager.get_knowledge_base_by_id(self.current_kb_id)
            self.update_stats_display(kb)
            
            if result["success"]:
                messagebox.showinfo(
                    "Succès",
                    f"Indexation terminée !\n{result['files_processed']} fichiers traités\n{result['chunks_created']} chunks créés"
                )
            else:
                messagebox.showwarning(
                    "Attention",
                    f"Indexation terminée avec des erreurs:\n" + "\n".join(result["errors"][:5])
                )
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'indexation: {str(e)}")
    
    def _ingest_file_thread(self, file_path: str):
        """Ingest file in background thread."""
        def progress_callback(message: str, progress: float):
            self.progress_label.configure(text=message)
            self.progress_bar.set(progress)
        
        try:
            result = self.ingestion_service.ingest_file(
                self.current_kb_id,
                file_path,
                progress_callback
            )
            
            # Update stats
            kb = self.data_manager.get_knowledge_base_by_id(self.current_kb_id)
            current_doc_count = kb.get("document_count", 0) if kb else 0
            new_doc_count = current_doc_count + 1 if result["success"] else current_doc_count
            
            stats = self.vector_store.get_stats(self.current_kb_id)
            self.data_manager.update_knowledge_base(
                self.current_kb_id,
                chunk_count=stats["chunk_count"],
                document_count=new_doc_count
            )
            
            # Refresh display
            kb = self.data_manager.get_knowledge_base_by_id(self.current_kb_id)
            self.update_stats_display(kb)
            
            if result["success"]:
                messagebox.showinfo(
                    "Succès",
                    f"Fichier indexé !\n{result['chunks_created']} chunks créés"
                )
            else:
                messagebox.showerror(
                    "Erreur",
                    f"Erreur:\n" + "\n".join(result["errors"])
                )
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'indexation: {str(e)}")
    
    def delete_kb(self, kb_id: str, kb_name: str):
        """Delete a knowledge base."""
        confirm = messagebox.askyesno(
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer '{kb_name}' ?\nCette action est irréversible."
        )
        
        if not confirm:
            return
        
        try:
            # Delete from vector store
            self.vector_store.delete_knowledge_base(kb_id)
            
            # Delete from data manager
            self.data_manager.delete_knowledge_base(kb_id)
            
            messagebox.showinfo("Succès", f"Base '{kb_name}' supprimée")
            self.show_list_view()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
