\set ON_ERROR_STOP on
BEGIN READ ONLY;
SELECT json_build_object(
  'public_tables', (SELECT count(*) FROM pg_tables WHERE schemaname='public'),
  'users', (SELECT count(*) FROM public.iam_user),
  'role_assignments', (SELECT count(*) FROM public.iam_roleassignment),
  'frameworks', (SELECT count(*) FROM public.core_framework),
  'compliance_assessments', (SELECT count(*) FROM public.core_complianceassessment),
  'assets', (SELECT count(*) FROM public.core_asset),
  'evidence', (SELECT count(*) FROM public.core_evidence)
);
COMMIT;
