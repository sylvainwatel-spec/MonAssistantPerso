"""
Results Manager - Gestion des résultats de scraping.
Sauvegarde et charge les résultats de ScrapeGraphAI dans des fichiers JSON.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class ResultsManager:
    """Gestionnaire de sauvegarde et chargement des résultats de scraping."""
    
    def __init__(self, results_dir: str = "resultats"):
        """
        Initialise le gestionnaire de résultats.
        
        Args:
            results_dir: Répertoire où stocker les résultats (par défaut: "resultats")
        """
        # Construire le chemin absolu du répertoire de résultats
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.results_dir = os.path.join(base_dir, results_dir)
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(self.results_dir, exist_ok=True)
    
    def save_result(self, data: Dict[str, Any]) -> str:
        """
        Sauvegarde un résultat de scraping dans un fichier JSON.
        
        Args:
            data: Dictionnaire contenant les données à sauvegarder
                  Doit contenir au minimum: assistant_id, query, results
        
        Returns:
            Chemin absolu du fichier créé
        """
        # Générer un nom de fichier unique avec timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        assistant_id = data.get("assistant_id", "unknown")
        filename = f"scraping_{assistant_id}_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        # Ajouter le timestamp si pas déjà présent
        if "timestamp" not in data:
            data["timestamp"] = datetime.datetime.now().isoformat()
        
        # Sauvegarder dans le fichier
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_result(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Charge un résultat depuis un fichier JSON.
        
        Args:
            filepath: Chemin du fichier à charger
        
        Returns:
            Dictionnaire contenant les données, ou None si erreur
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de {filepath}: {e}")
            return None
    
    def get_recent_results(self, assistant_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Récupère les N résultats les plus récents pour un assistant.
        
        Args:
            assistant_id: ID de l'assistant
            limit: Nombre maximum de résultats à retourner
        
        Returns:
            Liste des résultats, triés du plus récent au plus ancien
        """
        results = []
        
        # Lister tous les fichiers de l'assistant
        pattern = f"scraping_{assistant_id}_*.json"
        files = []
        
        for filename in os.listdir(self.results_dir):
            if filename.startswith(f"scraping_{assistant_id}_") and filename.endswith(".json"):
                filepath = os.path.join(self.results_dir, filename)
                # Récupérer la date de modification
                mtime = os.path.getmtime(filepath)
                files.append((filepath, mtime))
        
        # Trier par date de modification (plus récent en premier)
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Charger les N premiers fichiers
        for filepath, _ in files[:limit]:
            data = self.load_result(filepath)
            if data:
                results.append(data)
        
        return results
    
    def get_all_results(self, assistant_id: str) -> List[Dict[str, Any]]:
        """
        Récupère tous les résultats pour un assistant.
        
        Args:
            assistant_id: ID de l'assistant
        
        Returns:
            Liste de tous les résultats, triés du plus récent au plus ancien
        """
        return self.get_recent_results(assistant_id, limit=999999)
    
    def cleanup_old_results(self, days: int = 30) -> int:
        """
        Supprime les résultats plus anciens que N jours.
        
        Args:
            days: Nombre de jours (les fichiers plus anciens seront supprimés)
        
        Returns:
            Nombre de fichiers supprimés
        """
        count = 0
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
        cutoff_timestamp = cutoff_time.timestamp()
        
        for filename in os.listdir(self.results_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.results_dir, filename)
                mtime = os.path.getmtime(filepath)
                
                if mtime < cutoff_timestamp:
                    try:
                        os.remove(filepath)
                        count += 1
                    except Exception as e:
                        print(f"Erreur lors de la suppression de {filepath}: {e}")
        
        return count
    
    def get_results_summary(self, assistant_id: str) -> Dict[str, Any]:
        """
        Obtient un résumé des résultats pour un assistant.
        
        Args:
            assistant_id: ID de l'assistant
        
        Returns:
            Dictionnaire avec statistiques (nombre total, date du plus récent, etc.)
        """
        results = self.get_all_results(assistant_id)
        
        if not results:
            return {
                "total_count": 0,
                "most_recent": None,
                "oldest": None
            }
        
        return {
            "total_count": len(results),
            "most_recent": results[0].get("timestamp") if results else None,
            "oldest": results[-1].get("timestamp") if results else None,
            "queries": [r.get("query") for r in results if r.get("query")]
        }
