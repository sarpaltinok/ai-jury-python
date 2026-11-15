import json
import os
import time
from dotenv import load_dotenv
import litellm
from litellm import completion

load_dotenv()

litellm.drop_params = True
litellm.suppress_debug_info = True
litellm.set_verbose = False

CONFIG_FILE = "config.json"
PROFILE_FILE = "profile.json"


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Yapılandırma dosyası bulunamadı: {CONFIG_FILE}")
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_profile() -> dict:
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
    history = profile_data.get("ogrenilen_gercekler_ve_karar_gecmisi", [])
    if isinstance(history, list) and len(history) > max_items:
        profile_data["ogrenilen_gercekler_ve_karar_gecmisi"] = history[-max_items:]

    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=2)


def call_llm(
    prompt: str,
    system_instruction: str,
    primary_model: str,
    fallback_models: list[str],
    temperature: float = 0.4,
    json_mode: bool = False,
) -> str:
    """Herhangi bir LLM sağlayıcısına istek atar; 503/429 hatalarında otomatik retry ve fallback yapar."""
    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt},
    ]

    kwargs = {
        "model": primary_model,
        "messages": messages,
        "temperature": temperature,
        "num_retries": 2,
        "fallbacks": fallback_models,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = completion(**kwargs)
    return response.choices[0].message.content.strip()


def update_memory(
    user_idea: str,
    jury_summary: str,
    current_profile: dict,
    primary_model: str,
    fallback_models: list[str],
    max_items: int,
):
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

    raw_reply = call_llm(
        prompt=prompt,
        system_instruction=updater_instruction,
        primary_model=primary_model,
        fallback_models=fallback_models,
        temperature=0.1,
        json_mode=True,
    )

    try:
        updated_data = json.loads(raw_reply)
        save_profile(updated_data, max_items=max_items)
        print("\n[Sistem]: Kişisel profil hafızası güncellendi.")
    except Exception as e:
        print(f"\n[Sistem Uyarısı]: Hafıza güncellenirken format hatası oluştu: {e}")


def run_jury(user_idea: str):
    config = load_config()
    primary_model = config.get("primary_model", "gemini/gemini-3.8-flash")
    fallback_models = config.get("fallback_models", [])
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
        system_instruction = agent["role"]
        if agent.get("use_profile", False):
            system_instruction = f"{profile_context}{system_instruction}"

        # İstersen config.json içinde ajan bazlı özel model de tanımlayabilirsin
        agent_model = agent.get("model", primary_model)

        prompt = (
            f"{discussion_history}\n"
            f"Sıra sende ({agent['name']}). Yukarıdaki tartışmayı dikkate alarak değerlendirmeni yap:"
        )

        reply = call_llm(
            prompt=prompt,
            system_instruction=system_instruction,
            primary_model=agent_model,
            fallback_models=fallback_models,
            temperature=0.4,
        )

        profile_tag = " [Profil Aktif]" if agent.get("use_profile", False) else " [Evrensel]"
        print(f"[{agent['name']}{profile_tag}]:\n{reply}\n")
        print("-" * 60)

        discussion_history += f"\n[{agent['name']}]:\n{reply}\n"
        if agent["name"] == "Bas_Hakem":
            final_verdict = reply

    update_memory(user_idea, final_verdict, profile, primary_model, fallback_models, max_memory_items)


if __name__ == "__main__":
    idea = input("\nKurula danışmak istediğin konuyu veya kararını yaz:\n> ")
    if idea.strip():
        try:
            run_jury(idea)
        except Exception as e:
            print(f"\n[Hata]: {e}")