# AI Jury

Bu proje, kullanıcıların kararlarını veya fikirlerini farklı bakış açılarıyla değerlendiren bir "yapay zekâ jürisi" örneğidir. Kullanıcıdan gelen fikir, karar veya öneri için birden fazla AI ajanı tartışır; ardından bir baş hakem nihai kararı sunar.

Amaç, tek bir cevap yerine, risk, fırsat, gerçekçilik ve objektiflik gibi farklı yönleri birlikte değerlendiren bir karar desteği üretmektir.

## Özellikler

- Çoklu ajan yaklaşımı:
  - Opportunity Analyst
  - Devil Advocate
  - Practical Realist
  - Chief Judge
- Kullanıcı profili hafızası
- Karar sonrası öğrenme ve kişisel profil güncelleme
- Google Gemini tabanlı yapay zeka entegrasyonu
- Konfigürasyon tabanlı ajan tanımları
- Python ile kolay çalıştırılabilir yapı

## Nasıl Çalışır?

1. Kullanıcı bir fikir veya karar yazar.
2. Sistem, yapılandırılmış ajanları sırayla çalıştırır.
3. Her ajan kararın farklı yönünü değerlendirir.
4. Son aşamada Chief Judge nihai karar raporunu üretir.
5. Sonuç, kullanıcı profilini güncellemek için hafıza mekanizmasına iletilir.

## Proje Yapısı

```text
ai-jury-python/
├── main.py
├── config.json
├── profile.json
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Kurulum

1. Projeyi klonlayın:

```bash
git clone <repo-url>
cd ai-jury-python
```

2. Sanal ortam oluşturun:

```bash
python -m venv venv
```

3. Sanal ortamı aktif edin:

- Windows:

```bash
venv\Scripts\activate
```

- macOS/Linux:

```bash
source venv/bin/activate
```

4. Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

5. Ortam değişkenini ekleyin:

Oluşturduğunuz `.env` dosyasına aşağıdaki satırı ekleyin:

```env
GEMINI_API_KEY=your_api_key_here
```

## Çalıştırma

```bash
python main.py
```

Program çalıştığında kullanıcıdan karar veya fikir istenir. Sonrasında kurul tartışması başlar.

## Yapılandırma

Ajanlar ve temel ayarlar `config.json` dosyasında bulunur.

Örnek yapı:

```json
{
  "model_id": "gemini-3.8-flash",
  "max_memory_items": 10,
  "agents": [
    {
      "name": "Opportunity_Analyst",
      "use_profile": false,
      "role": "..."
    },
    {
      "name": "Devil_Advocate",
      "use_profile": false,
      "role": "..."
    },
    {
      "name": "Practical_Realist",
      "use_profile": true,
      "role": "..."
    },
    {
      "name": "Chief_Judge",
      "use_profile": true,
      "role": "..."
    }
  ]
}
```

### `use_profile` nedir?

- `true` ise ajan, kullanıcı profil bağlamını tartışmaya dahil eder.
- `false` ise ajan daha genel ve evrensel bir bakış açısıyla konuşur.

## Hafıza Sistemi

Uygulama, `profile.json` dosyasında kullanıcıya ait hafızayı saklar. Bu hafıza şu alanları içerir:

- kimlik ve yaşam bağlamı
- finansal durum
- zaman ve enerji kısıtları
- değerler ve öncelikler
- alışkanlıklar ve rutinler
- öğrenilen gerçekler ve karar geçmişi

Bu sistem, kararlar sonrası ortaya çıkan kalıcı bilgileri bir sonraki değerlendirmede kullanır.

## Örnek Kullanım

```text
Kurula danışmak istediğin konuyu veya kararını yaz:
> Yatırım yapmalı mıyım?
```

Sonrasında düzenlenen jüriden aşağıya benzer çıktılar alınabilir:

- Opportunity Analyst: Fırsat ve uzun vadeli değer
- Devil Advocate: Riskler ve olası maliyetler
- Practical Realist: Pratik uygulanabilirlik
- Chief Judge: Nihai karar ve gerekçelendirme

## Geliştirme Fikirleri

- Ajan rolleri için daha derin ve uzmanlaştırılmış karakterler eklenebilir.
- Çoklu dil desteği oluşturulabilir.
- Daha güçlü arka plan hafızası sistemi eklenebilir.
- Sonuçlar için JSON çıktısı yerine daha iyi formatlı rapor üretimi yapılabilir.
- Web arayüzü veya FastAPI tabanlı API katmanı eklenebilir.

## Gereksinimler

- Python 3.10+
- Google Gemini API anahtarı
- `python-dotenv`
- `google-genai`

## Lisans

Bu proje MIT Lisansı altında yayımlanmıştır.

MIT License

Copyright (c) 2026 AI Jury

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Katkı

Katkı sağlamak isterseniz:

1. Fork yapın
2. Yeni bir branch açın
3. Değişikliklerinizi yapın
4. Pull request oluşturun

---

Projeyi daha da geliştirmek için yeni ajan rolleri, daha güçlü hafıza sistemi ya da web arayüzü eklenebilir.
