CREATE OR REPLACE FUNCTION notify_certificate_changes()
    RETURNS trigger AS
    $$
    DECLARE
    source_value text;
    expected_source_value text := 'rabbitmq';
    BEGIN
        SELECT current_setting('custom_variable.source_session', 't') INTO source_value;
        IF source_value IS NOT NULL AND source_value = expected_source_value THEN
            RESET custom_variable.source_session;
            RETURN NULL;
        ELSE
            PERFORM pg_notify(
                    'certificate_notify_trigger',
                    json_build_object(
                            'table', TG_TABLE_NAME,
                            'operation', TG_OP,
                            'new_record', row_to_json(NEW),
                            'old_record', row_to_json(OLD),
                            'source_id', 'postgres_env2'::text
                    
                        )::text
                );

            RETURN NEW;
        END IF;
    END;
    $$ LANGUAGE plpgsql;
        
    CREATE OR REPLACE TRIGGER certificate_notify_trigger
    AFTER INSERT OR UPDATE OR DELETE ON certificates
    FOR EACH ROW 
    EXECUTE PROCEDURE notify_certificate_changes();

ALTER TABLE certificates
ALTER COLUMN id DROP IDENTITY;
CREATE SEQUENCE IF NOT EXISTS three_step_id_seq START 2 INCREMENT 3;    
ALTER TABLE certificates
ALTER COLUMN id SET DEFAULT nextval('three_step_id_seq');