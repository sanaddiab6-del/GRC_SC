import FrameworkPage from '@/components/FrameworkPage';

export default function ECCFrameworkPage() {
  return (
    <FrameworkPage
      frameworkCode="ECC"
      frameworkName={{
        en: "Essential Cybersecurity Controls (ECC)",
        ar: "الضوابط الأساسية للأمن السيبراني"
      }}
      organizationName={{
        en: "National Cybersecurity Authority - Saudi Arabia",
        ar: "الهيئة الوطنية للأمن السيبراني - المملكة العربية السعودية"
      }}
      description={{
        en: "The Essential Cybersecurity Controls (ECC) are a set of mandatory security controls issued by the National Cybersecurity Authority of Saudi Arabia. These controls aim to protect the Kingdom's critical infrastructure and digital assets.",
        ar: "الضوابط الأساسية للأمن السيبراني (ECC) هي مجموعة من الضوابط الأمنية الإلزامية الصادرة عن الهيئة الوطنية للأمن السيبراني في المملكة العربية السعودية. تهدف هذه الضوابط إلى حماية البنية التحتية الحيوية والأصول الرقمية للمملكة."
      }}
      gradientColors="from-blue-600 to-blue-800"
      emoji="🛡️"
      highlightColor="blue"
    />
  );
}
