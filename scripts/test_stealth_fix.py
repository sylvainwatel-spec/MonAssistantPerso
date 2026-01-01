import os
import sys

# Ajouter le dossier parent au path pour les imports si besoin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("🚀 Test d'import de playwright_stealth...")
    from playwright_stealth import Stealth
    print("✅ Import réussi: from playwright_stealth import Stealth")
    
    from playwright.sync_api import sync_playwright
    
    print("🚀 Lancement de Playwright pour test d'application...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        print("🛠️ Tentative d'application de Stealth().apply_stealth_sync(context)...")
        stealth = Stealth()
        stealth.apply_stealth_sync(context)
        print("✅ Stealth appliqué avec succès au contexte !")
        
        page = context.new_page()
        print("📄 Page créée dans le contexte stealth.")
        
        # Petit test rapide
        webdriver = page.evaluate("navigator.webdriver")
        print(f"🕵️ navigator.webdriver = {webdriver}")
        
        if webdriver is None or webdriver is False:
            print("✅ TEST RÉUSSI : navigator.webdriver est masqué/falsifié")
        else:
            print("⚠️ NOTE : navigator.webdriver est encore visible (peut dépendre de la version), mais pas d'erreur au moins.")

        browser.close()
        print("🏁 Fin du test sans crash.")

except Exception as e:
    print(f"❌ ÉCHEC DU TEST : {e}")
    import traceback
    traceback.print_exc()
