import FrameworkPage from '@/components/FrameworkPage';

export default function CCCFrameworkPage() {
  return (
    <FrameworkPage
      frameworkCode="CCC"
      frameworkName={{
        en: "Cloud Cybersecurity Controls (CCC)",
        ar: "ضوابط الأمن السيبراني السحابي"
      }}
      organizationName={{
        en: "National Cybersecurity Authority - Saudi Arabia",
        ar: "الهيئة الوطنية للأمن السيبراني - المملكة العربية السعودية"
      }}
      description={{
        en: "The Cloud Cybersecurity Controls (CCC) are specialized controls for cloud computing issued by the National Cybersecurity Authority. These controls focus on protecting cloud data and services.",
        ar: "ضوابط الأمن السيبراني السحابي (CCC) هي مجموعة من الضوابط المتخصصة للحوسبة السحابية الصادرة عن الهيئة الوطنية للأمن السيبراني. تركز هذه الضوابط على حماية البيانات والخدمات السحابية."
      }}
      gradientColors="from-purple-600 to-purple-800"
      emoji="☁️"
      highlightColor="purple"
    />
  );
}
