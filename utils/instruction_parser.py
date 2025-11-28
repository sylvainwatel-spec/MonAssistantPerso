"""
Module pour parser les instructions URL en format texte structuré.

Format attendu:
SEARCH_INPUT: selector
SEARCH_BUTTON: selector (optionnel)
WAIT_FOR: selector (optionnel)
BEFORE_SEARCH:
  - CLICK: selector
  - WAIT: duration
RESULTS: selector (optionnel)
EXTRACT:
  - field_name: selector
"""

import re
import logging


class InstructionParser:
    """Parse les instructions URL en format texte vers un dictionnaire structuré."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse(self, text):
        """
        Parse le texte d'instructions et retourne un dictionnaire.
        
        Args:
            text (str): Texte d'instructions au format défini
            
        Returns:
            dict: Instructions parsées avec les clés:
                - search_input: sélecteur CSS pour le champ de recherche
                - search_button: sélecteur CSS pour le bouton de recherche (optionnel)
                - wait_for: sélecteur CSS à attendre après la recherche (optionnel)
                - before_search: liste d'actions à exécuter avant la recherche
                - results: sélecteur CSS pour les résultats (optionnel)
                - extract: dictionnaire {field_name: selector} pour l'extraction structurée
        """
        if not text or not text.strip():
            return {}
        
        result = {}
        lines = text.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):  # Ignorer les lignes vides et commentaires
                continue
            
            # Détection des sections principales
            if line.startswith('SEARCH_INPUT:'):
                result['search_input'] = line.split(':', 1)[1].strip()
                self.logger.debug(f"Parsed SEARCH_INPUT: {result['search_input']}")
                
            elif line.startswith('SEARCH_BUTTON:'):
                result['search_button'] = line.split(':', 1)[1].strip()
                self.logger.debug(f"Parsed SEARCH_BUTTON: {result['search_button']}")
                
            elif line.startswith('WAIT_FOR:'):
                result['wait_for'] = line.split(':', 1)[1].strip()
                self.logger.debug(f"Parsed WAIT_FOR: {result['wait_for']}")
                
            elif line.startswith('RESULTS:'):
                result['results'] = line.split(':', 1)[1].strip()
                self.logger.debug(f"Parsed RESULTS: {result['results']}")
                
            elif line.startswith('BEFORE_SEARCH:'):
                current_section = 'before_search'
                result['before_search'] = []
                self.logger.debug("Starting BEFORE_SEARCH section")
                
            elif line.startswith('EXTRACT:'):
                current_section = 'extract'
                result['extract'] = {}
                self.logger.debug("Starting EXTRACT section")
                
            elif line.startswith('-') and current_section:
                # Élément de liste
                item = line[1:].strip()
                if current_section == 'before_search':
                    self._parse_action(item, result['before_search'])
                elif current_section == 'extract':
                    self._parse_extract(item, result['extract'])
            else:
                # Ligne non reconnue, on l'ignore
                self.logger.debug(f"Ignoring unrecognized line: {line}")
        
        self.logger.info(f"Parsed instructions: {result}")
        return result
    
    def _parse_action(self, item, actions_list):
        """
        Parse une action de la section BEFORE_SEARCH.
        
        Formats supportés:
        - CLICK: selector
        - WAIT: duration (ex: 2s, 1000ms, 2)
        - TYPE: selector, text
        """
        if ':' not in item:
            self.logger.warning(f"Invalid action format (missing ':'): {item}")
            return
        
        action_type, value = item.split(':', 1)
        action_type = action_type.strip().upper()
        value = value.strip()
        
        if action_type == 'CLICK':
            actions_list.append({
                'type': 'click',
                'selector': value
            })
            self.logger.debug(f"Added CLICK action: {value}")
            
        elif action_type == 'WAIT':
            # Parser la durée (2s, 1000ms, ou juste un nombre en secondes)
            duration = self._parse_duration(value)
            actions_list.append({
                'type': 'wait',
                'duration': duration
            })
            self.logger.debug(f"Added WAIT action: {duration}ms")
            
        elif action_type == 'TYPE':
            # Format: selector, text
            if ',' in value:
                selector, text = value.split(',', 1)
                actions_list.append({
                    'type': 'type',
                    'selector': selector.strip(),
                    'text': text.strip()
                })
                self.logger.debug(f"Added TYPE action: {selector.strip()} -> {text.strip()}")
            else:
                self.logger.warning(f"Invalid TYPE action format (missing ','): {value}")
        else:
            self.logger.warning(f"Unknown action type: {action_type}")
    
    def _parse_duration(self, duration_str):
        """
        Parse une durée et retourne la valeur en millisecondes.
        
        Formats supportés:
        - "2s" -> 2000ms
        - "1000ms" -> 1000ms
        - "2" -> 2000ms (par défaut en secondes)
        """
        duration_str = duration_str.strip().lower()
        
        if duration_str.endswith('ms'):
            return int(duration_str[:-2])
        elif duration_str.endswith('s'):
            return int(float(duration_str[:-1]) * 1000)
        else:
            # Par défaut, on considère que c'est en secondes
            return int(float(duration_str) * 1000)
    
    def _parse_extract(self, item, extract_dict):
        """
        Parse un champ d'extraction de la section EXTRACT.
        
        Format: field_name: selector
        """
        if ':' not in item:
            self.logger.warning(f"Invalid extract format (missing ':'): {item}")
            return
        
        field, selector = item.split(':', 1)
        field = field.strip()
        selector = selector.strip()
        
        extract_dict[field] = selector
        self.logger.debug(f"Added extract field: {field} -> {selector}")
    
    def validate(self, parsed_instructions):
        """
        Valide les instructions parsées.
        
        Returns:
            tuple: (is_valid: bool, errors: list)
        """
        errors = []
        
        # Vérifier que les sélecteurs CSS sont valides (basique)
        for key in ['search_input', 'search_button', 'wait_for', 'results']:
            if key in parsed_instructions:
                selector = parsed_instructions[key]
                if not selector or not isinstance(selector, str):
                    errors.append(f"Invalid selector for {key}: {selector}")
        
        # Vérifier les actions
        if 'before_search' in parsed_instructions:
            for i, action in enumerate(parsed_instructions['before_search']):
                if 'type' not in action:
                    errors.append(f"Action {i} missing 'type' field")
                elif action['type'] == 'click' and 'selector' not in action:
                    errors.append(f"CLICK action {i} missing 'selector'")
                elif action['type'] == 'wait' and 'duration' not in action:
                    errors.append(f"WAIT action {i} missing 'duration'")
                elif action['type'] == 'type' and ('selector' not in action or 'text' not in action):
                    errors.append(f"TYPE action {i} missing 'selector' or 'text'")
        
        # Vérifier les champs d'extraction
        if 'extract' in parsed_instructions:
            for field, selector in parsed_instructions['extract'].items():
                if not selector or not isinstance(selector, str):
                    errors.append(f"Invalid selector for extract field '{field}': {selector}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
