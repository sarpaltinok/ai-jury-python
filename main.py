import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# .env dosyasındaki GEMINI_API_KEY değerini yükler
load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL_ID = "gemini-3.8-flash"  # Daha derin analiz için "gemini-3.8-pro" yapabilirsin

# Jüri Üyeleri (Ajanlar ve Karakteristik Sistem Talimatları)
AGENTS = [
    {
        "name": "Firsat_Analisti",
        "role": (
            "Sen uzun vadeli büyüme, kariyer gelişimi ve yaşam kalitesine odaklanan stratejik bir danışmansın. "
            "Kullanıcının sunduğu kararın yaratabileceği fırsatları, kazandıracağı deneyimleri ve pozitif potansiyeli "
            "somut gerekçelerle savun. Duygusal gaz verme, rasyonel faydaları ortaya koy. Maksimum 2 paragraf yaz."
        ),
    },
    {
        "name": "Seytanin_Avukati",
        "role": (
            "Sen acımasız bir gerçekçi ve risk analistisin. Kullanıcıya kesinlikle yalakalık yapma veya onaylama eğilimine girme. "
            "Önceki konuşmacının iyimser yorumlarını da çürüterek; kararın gizli maliyetlerini, zaman kaybını, stres faktörlerini "
            "ve ters gidebilecek en kötü senaryoları sert ve doğrudan bir dille yüzüne vur. Maksimum 2 paragraf yaz."
        ),
    },
    {
        "name": "Pratik_Gercekci",
        "role": (
            "Sen günlük hayatın pratiklerine, enerji yönetimine ve sürdürülebilirliğe odaklanan bir uzmansın. "
            "Önceki iki konuşmacının söylediklerini değerlendir ve bu kararın kullanıcının mevcut rutinine, bütçesine ve "
            "zamanına gerçekte nasıl oturacağını sorgula. 'Teoride güzel ama pratikte 2 hafta sonra tıkanır mı?' sorusuna odaklan. Maksimum 2 paragraf yaz."
        ),
    },
    {
        "name": "Bas_Hakem",
        "role": (
            "Sen duygusallıktan uzak, tamamen objektif bir karar mercisin. Fırsat Analisti, Şeytanın Avukatı ve "
            "Pratik Gerçekçi'nin tüm argümanlarını tart. Kullanıcının kendi kendini kandırdığı kör noktaları tespit et. "
            "Tartışma sonunda net bir 'KARAR: YAP / YAPMA / ŞU ŞARTLARLA YAP' başlığıyla gerekçeli nihai raporunu sun."
        ),
    },
]


def run_jury(user_idea: str):
    print(f"\n--- KARAR KURULU TOPLANDI ---\nKonu: {user_idea}\n" + "=" * 60 + "\n")

    # Tüm ajanların birbirinin söylediklerini görebilmesi için ortak tartışma geçmişi
    discussion_history = f"KULLANICININ DANIŞTIĞI KARAR/FİKİR:\n{user_idea}\n\n--- TARTIŞMA KAYDI ---\n"

    for agent in AGENTS:
        prompt = (
            f"{discussion_history}\n"
            f"Sıra sende ({agent['name']}). Yukarıdaki tartışmayı dikkate alarak kendi rolüne uygun değerlendirmeni yap:"
        )

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=agent["role"],
                temperature=0.4,
            ),
        )

        reply = response.text.strip()
        print(f"[{agent['name']}]:\n{reply}\n")
        print("-" * 60)

        # Ajanın cevabını ortak hafızaya ekle ki bir sonraki ajan bunu okuyup cevap verebilsin
        discussion_history += f"\n[{agent['name']}]:\n{reply}\n"


if __name__ == "__main__":
    idea = input("\nKurula danışmak istediğin konuyu veya kararını yaz:\n> ")
    if idea.strip():
        run_jury(idea)