import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
CONFIG_FILE = "config.json"
PROFILE_FILE = "profile.json"


def load_config() -> dict:
    """Uygulama ve ajan yapılandırmasını config.json dosyasından okur."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Yapılandırma dosyası bulunamadı: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_profile() -> dict:
    """Genel amaçlı, konu bağımsız kullanıcı profilini yükler veya oluşturur."""
    if not os.path.exists(PROFILE_FILE):
        initial_profile = {
            "kimlik_ve_yasam_baglami": "Belirtilmedi",
            "kaynaklar_ve_kisitlar": {
                "finansal_durum": "Belirtilmedi",
                "zaman_ve_enerji": "Belirtilmedi"
            },
            "degerler_ve_oncelikler": [],
            "aliskanliklar_ve_rutinler": [],
            "ogrenilen_gercekler_ve_karar_gecmisi": []
        }
        save_profile(initial_profile)
        return initial_profile

    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(profile_data: dict, max_items: int = 10):
    """Profili kaydeder ve geçmiş listesini belirlenen maksimum eleman sayısıyla sınırlar (Sliding Window)."""
    history = profile_data.get("ogrenilen_gercekler_ve_karar_gecmisi", [])
    if isinstance(history, list) and len(history) > max_items:
        profile_data["ogrenilen_gercekler_ve_karar_gecmisi"] = history[-max_items:]

    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=2)


def update_memory(user_idea: str, jury_summary: str, current_profile: dict, model_id: str, max_items: int):
    """Tartışma sonunda konu bağımsız olarak öğrenilen kalıcı gerçekleri profile işler."""
    updater_instruction = (
        "Sen bir arka plan hafıza yöneticisisin. Sana kullanıcının mevcut profil JSON'ı, "
        "yeni sorduğu soru ve kurulun verdiği karar özeti verilecek. "
        "Kullanıcının sorusundan veya kurul kararından; finansal durum, zaman/enerji kısıtları, "
        "değerler/öncelikler, rutinler veya yeni alınan/ertelenen kararlar hakkında kalıcı bir bilgi çıktıysa "
        "ilgili alanları güncelle veya 'ogrenilen_gercekler_ve_karar_gecmisi' listesine kısa, öz bir madde ekle. "
        f"Listede en fazla {max_items} madde tut; gereksiz veya güncelliğini yitirmiş olanları çıkar. "
        "Geçici detayları ekleme; yeni bir bilgi yoksa mevcut JSON'ı aynen döndür. "
        "SADECE geçerli bir JSON çıktısı ver, başka hiçbir açıklama veya markdown bloğu ekleme."
    )

    prompt = (
        f"MEVCUT PROFİL:\n{json.dumps(current_profile, ensure_ascii=False)}\n\n"
        f"KULLANICININ YENİ SORUSU:\n{user_idea}\n\n"
        f"KURUL KARARI:\n{jury_summary}"
    )

    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=updater_instruction,
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )

    try:
        updated_data = json.loads(response.text.strip())
        save_profile(updated_data, max_items=max_items)
        print("\n[Sistem]: Kişisel profil hafızası güncellendi.")
    except Exception as e:
        print(f"\n[Sistem Uyarısı]: Hafıza güncellenirken format hatası oluştu: {e}")


def run_jury(user_idea: str):
    config = load_config()
    model_id = config.get("model_id", "gemini-3.8-flash")
    max_memory_items = config.get("max_memory_items", 10)
    agents_config = config.get("agents", [])

    profile = load_profile()
    profile_context = (
        "ARKA PLAN KULLANICI PROFİLİ (Sadece sorulan konuyla DOĞRUDAN ilgiliyse referans al. "
        "Konuyla ilgisiz profil detaylarını tartışmaya zorla dahil etme; önce sorunun kendi mantığını değerlendir):\n"
        f"{json.dumps(profile, ensure_ascii=False, indent=2)}\n\n"
    )

    print(f"\n--- KARAR KURULU TOPLANDI ---\nKonu: {user_idea}\n" + "=" * 60 + "\n")
    discussion_history = f"KULLANICININ DANIŞTIĞI KARAR/FİKİR:\n{user_idea}\n\n--- TARTIŞMA KAYDI ---\n"
    final_verdict = ""

    for agent in agents_config:
        # Sadece config'de use_profile=true olan ajanlara profil bağlamını ekle
        system_instruction = agent["role"]
        if agent.get("use_profile", False):
            system_instruction = f"{profile_context}{system_instruction}"

        prompt = (
            f"{discussion_history}\n"
            f"Sıra sende ({agent['name']}). Yukarıdaki tartışmayı dikkate alarak değerlendirmeni yap:"
        )

        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.4,
            ),
        )

        reply = response.text.strip()
        profile_tag = " [Profil Aktif]" if agent.get("use_profile", False) else " [Evrensel]"
        print(f"[{agent['name']}{profile_tag}]:\n{reply}\n")
        print("-" * 60)

        discussion_history += f"\n[{agent['name']}]:\n{reply}\n"
        if agent["name"] == "Chief_Judge":
            final_verdict = reply

    update_memory(user_idea, final_verdict, profile, model_id, max_memory_items)


if __name__ == "__main__":
    idea = input("\nKurula danışmak istediğin konuyu veya kararını yaz:\n> ")
    if idea.strip():
        run_jury(idea)