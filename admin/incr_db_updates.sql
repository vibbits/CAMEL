--
-- Alterations to the DB schema (`dbschema.sql`) will in
-- the same commit be described here, so they can be applied to
-- a  populated database.
-- 

ALTER TABLE `fields` MODIFY COLUMN `type_column` enum('value_VARCHAR','value_TEXT','value_INT','value_DOUBLE','value_BOOL', 'value_ATTACH');
ALTER TABLE `experiments_fields` ADD COLUMN `value_ATTACH` varchar(255);
