# Generated manually to fix library imports for frameworks with missing optional fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0151_add_riskmatrix_editing_fields"),
    ]

    operations = [
        migrations.RunSQL(
            sql=r"""
ALTER TABLE core_framework
ALTER COLUMN outcomes_definition SET DEFAULT '[]'::jsonb;

ALTER TABLE core_framework
ALTER COLUMN editing_version SET DEFAULT 1;

ALTER TABLE core_framework
ALTER COLUMN editing_history SET DEFAULT '[]'::jsonb;

ALTER TABLE core_framework
ALTER COLUMN field_visibility SET DEFAULT '{}'::jsonb;

UPDATE core_framework
SET
    outcomes_definition = COALESCE(outcomes_definition, '[]'::jsonb),
    editing_version = COALESCE(editing_version, 1),
    editing_history = COALESCE(editing_history, '[]'::jsonb),
    field_visibility = COALESCE(field_visibility, '{}'::jsonb);

CREATE OR REPLACE FUNCTION fix_core_framework_import_defaults()
RETURNS trigger AS $$
BEGIN
    IF NEW.outcomes_definition IS NULL THEN
        NEW.outcomes_definition := '[]'::jsonb;
    END IF;

    IF NEW.editing_version IS NULL THEN
        NEW.editing_version := 1;
    END IF;

    IF NEW.editing_history IS NULL THEN
        NEW.editing_history := '[]'::jsonb;
    END IF;

    IF NEW.field_visibility IS NULL THEN
        NEW.field_visibility := '{}'::jsonb;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_fix_core_framework_import_defaults ON core_framework;

CREATE TRIGGER trg_fix_core_framework_import_defaults
BEFORE INSERT OR UPDATE ON core_framework
FOR EACH ROW
EXECUTE FUNCTION fix_core_framework_import_defaults();


ALTER TABLE core_requirementnode
ALTER COLUMN display_mode SET DEFAULT 'undefined';

UPDATE core_requirementnode
SET display_mode = 'undefined'
WHERE display_mode IS NULL;

CREATE OR REPLACE FUNCTION fix_core_requirementnode_import_defaults()
RETURNS trigger AS $$
BEGIN
    IF NEW.display_mode IS NULL THEN
        NEW.display_mode := 'undefined';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_fix_core_requirementnode_import_defaults ON core_requirementnode;

CREATE TRIGGER trg_fix_core_requirementnode_import_defaults
BEFORE INSERT OR UPDATE ON core_requirementnode
FOR EACH ROW
EXECUTE FUNCTION fix_core_requirementnode_import_defaults();
""",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
