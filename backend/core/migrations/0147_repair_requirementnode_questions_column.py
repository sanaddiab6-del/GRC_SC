from django.db import migrations


def add_questions_column_if_missing(apps, schema_editor):
    connection = schema_editor.connection
    table_name = "core_requirementnode"
    column_name = "questions"

    with connection.cursor() as cursor:
        columns = {
            col.name for col in connection.introspection.get_table_description(cursor, table_name)
        }
        if column_name not in columns:
            schema_editor.execute(
                "ALTER TABLE core_requirementnode ADD COLUMN questions jsonb NULL"
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0146_organisationobjective_closing_date_and_more"),
    ]

    operations = [
        migrations.RunPython(add_questions_column_if_missing, noop_reverse),
    ]