import FrameworkPage from '@/components/FrameworkPage';

export default function PDPLFrameworkPage() {
  return (
    <FrameworkPage
      frameworkCode="PDPL"
      frameworkName={{
        en: "Personal Data Protection Law (PDPL)",
        ar: "نظام حماية البيانات الشخصية"
      }}
      organizationName={{
        en: "Saudi Data & AI Authority (SDAIA)",
        ar: "الهيئة السعودية للبيانات والذكاء الاصطناعي (سدايا)"
      }}
      description={{
        en: "The Personal Data Protection Law (PDPL) is the main regulatory framework for data protection in Saudi Arabia. The law aims to protect individuals' privacy and regulate personal data processing.",
        ar: "نظام حماية البيانات الشخصية (PDPL) هو الإطار التنظيمي الرئيسي لحماية البيانات في المملكة العربية السعودية. يهدف النظام إلى حماية خصوصية الأفراد وتنظيم معالجة البيانات الشخصية."
      }}
      gradientColors="from-green-600 to-green-800"
      emoji="🔒"
      highlightColor="green"
    />
  );
}
