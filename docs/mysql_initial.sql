/* MySQL initial script */
--
-- Upgrade to 2.0
--
-- Empty the permission table
-- TRUNCATE auth_permission;
-- TRUNCATE auth_group_permissions;

-- Add columns new app need
ALTER TABLE test_plans ADD extra_link varchar(1024);
ALTER TABLE test_runs ADD estimated_time time DEFAULT '00:00:00';
ALTER TABLE test_attachments ADD stored_name mediumtext;

--
-- Upgrade to 3.0
--

-- Rename the columns name to fit the ORM
ALTER TABLE test_case_runs CHANGE assignee assignee_id mediumint(9);
ALTER TABLE test_case_runs CHANGE testedby tested_by_id mediumint(9);

-- Add WAIVED case run status(Bug #577272)
INSERT INTO test_case_run_status (name, sortkey, description) VALUES ('WAIVED', 8, NULL);

-- Add Primary Key to test case bugs and other necessary columns for outside bug system support
ALTER TABLE test_case_bugs ADD id int NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;
ALTER TABLE test_case_bugs ADD bug_system_id int NOT NULL;
ALTER TABLE test_case_bugs ADD summary varchar(255);
ALTER TABLE test_case_bugs ADD description mediumtext;
CREATE INDEX case_bugs_case_bug_system_id_idx ON test_case_bugs (bug_system_id);

-- After syncdb process
-- INSERT INTO test_case_bug_systems (name, url_reg_exp) values ('Red Hat Bugzilla', 'https://bugzilla.redhat.com/show_bug.cgi?id=%s');
-- UPDATE test_case_bugs SET bug_system_id = 1;
ALTER TABLE test_tags CHANGE tag_name tag_name VARCHAR(255) CHARACTER SET latin1 COLLATE latin1_general_cs;

-- Upgrade to 3.0.2
ALTER TABLE test_cases ADD is_automated_proposed tinyint(4) NOT NULL DEFAULT 0 AFTER isautomated;

-- Upgrade to 3.0.3
ALTER TABLE test_case_run_status ADD auto_blinddown tinyint(4) NOT NULL DEFAULT 1;
UPDATE test_case_run_status SET auto_blinddown = 0 WHERE name = 'RUNNING';

-- Upgrade to 3.0.4
ALTER TABLE test_cases ADD notes mediumtext;

-- Upgrade to 3.1.1
ALTER TABLE test_plans ADD COLUMN parent_id int unsigned;

-- Upgrade to 3.2
DROP TABLE IF EXISTS tcms_bookmark_categories;
DROP TABLE IF EXISTS tcms_bookmarks;
ALTER TABLE test_cases ADD reviewer_id int(11) NULL AFTER default_tester_id;

-- Upgrade to 3.5
ALTER TABLE test_case_plans ADD COLUMN sortkey int(11) default NULL;
ALTER TABLE test_case_plans ADD COLUMN id int NOT NULL AUTO_INCREMENT  primary key first;
ALTER TABLE test_cases DROP COLUMN sortkey;

-- Character set changes.
-- ALTER TABLE `testopia`.`auth_message` CHANGE COLUMN `message` `message` LONGTEXT CHARACTER SET 'utf8' NOT NULL ;
-- ALTER TABLE `testopia`.`auth_message` CHARACTER SET = utf8 ;
-- ALTER TABLE `testopia`.`test_tags` CHANGE COLUMN `tag_name` `tag_name` VARCHAR(255) CHARACTER SET 'utf8' DEFAULT NULL ;

-- TCMS 3.5, added a new column for test_plans
ALTER TABLE test_plans ADD column owner_id mediumint(9) DEFAULT null ;

-- TCMS 3.6.3, added a new column for test_runs
ALTER TABLE test_runs ADD column case_run_status varchar(100) DEFAULT '' ;
ALTER TABLE test_runs ADD column errata_id mediumint(9) DEFAULT NULL ;

-- TCMS 3.6.3, added triggers on test_case_runs
DELIMITER '|';
CREATE TRIGGER case_run_status_trigger_update
    AFTER UPDATE ON test_case_runs
    FOR EACH ROW BEGIN
        UPDATE test_runs SET case_run_status = (
            SELECT
                group_concat(concat(a.status, ':', a.count)) AS status_count
            FROM (
                SELECT 
                    case_run_status_id AS status,
                    count(*) AS count FROM test_case_runs
                WHERE
                    run_id = NEW.run_id
                GROUP BY case_run_status_id
                ORDER BY status
            ) AS a
        )
        WHERE run_id = NEW.run_id;
    END|

CREATE TRIGGER case_run_status_trigger_insert
    AFTER INSERT ON test_case_runs
    FOR EACH ROW BEGIN
        UPDATE test_runs SET case_run_status = (
            SELECT
                group_concat(concat(a.status, ':', a.count)) AS status_count
            FROM (
                SELECT 
                    case_run_status_id AS status,
                    count(*) AS count FROM test_case_runs
                WHERE
                    run_id = NEW.run_id
                GROUP BY case_run_status_id
                ORDER BY status
            ) AS a
        )
        WHERE run_id = NEW.run_id;
    END|

CREATE TRIGGER case_run_status_trigger_delete
    AFTER DELETE ON test_case_runs
    FOR EACH ROW BEGIN
        UPDATE test_runs SET case_run_status = (
            SELECT
                group_concat(concat(a.status, ':', a.count)) AS status_count
            FROM (
                SELECT 
                    case_run_status_id AS status,
                    count(*) AS count FROM test_case_runs
                WHERE
                    run_id = OLD.run_id
                GROUP BY case_run_status_id
                ORDER BY status
            ) AS a
        )
        WHERE run_id = OLD.run_id;
    END|
DELIMITER ';'|

-- TCMS 3.7
-- Due to Django's lack of support for united primary keys,
-- add primary key for tables that are not having primary keys
-- but just unite keys
ALTER TABLE test_case_texts ADD COLUMN id int(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE test_plan_texts ADD COLUMN id int(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT;

-- TCMS 3.7.2, hot-fix tag loss
-- Add primary key for tables that are relate tags
ALTER TABLE test_plan_tags ADD COLUMN id int(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE test_case_tags ADD COLUMN id int(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT;
ALTER TABLE test_run_tags ADD COLUMN id int(10) UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT;

-- TCMS 3.8, added a new column for test_plans
ALTER TABLE test_plans ADD column product_version_id mediumint(9) DEFAULT null ;
ALTER TABLE test_cases ADD column extra_link varchar(1024) DEFAULT null ;
ALTER TABLE test_runs ADD column auto_update_run_status boolean DEFAULT false;       
