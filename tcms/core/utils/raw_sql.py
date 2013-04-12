# -*- coding: utf-8 -*-
# 
# Nitrate is copyright 2010 Red Hat, Inc.
# 
# Nitrate is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version. This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranties of TITLE, NON-INFRINGEMENT,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
# The GPL text is available in the file COPYING that accompanies this
# distribution and at <http://www.gnu.org/licenses>.
# 
# Authors:
#   Xuqing Kuang <xkuang@redhat.com>
#   Lizhang Li <eli@redhat.com>

class RawSQL:
    """
    Record the Raw SQL for operate the database directly.
    """
    # Following SQL use for count case and run in plan
    num_cases = 'SELECT COUNT(*) \
        FROM test_case_plans \
        WHERE test_case_plans.plan_id = test_plans.plan_id'
    
    num_runs = 'SELECT COUNT(*) \
        FROM test_runs \
        WHERE test_runs.plan_id = test_plans.plan_id'
    
    num_plans = 'SELECT COUNT(*) \
        FROM test_plans AS ch_plans\
        WHERE ch_plans.parent_id = test_plans.plan_id'
    
    num_case_bugs = 'SELECT COUNT(*) \
        FROM test_case_bugs \
        WHERE test_case_bugs.case_id = test_cases.case_id'
    
    num_case_run_bugs = 'SELECT COUNT(*) \
        FROM test_case_bugs \
        WHERE test_case_bugs.case_run_id = test_case_runs.case_run_id'
    
    # Following SQL use for test case run
    completed_case_run_percent = 'SELECT ROUND(no_idle_count/total_count*100,0) \
        FROM ( \
            SELECT \
                tr1.run_id AS run_id, \
                count(tcr1.case_run_id) AS no_idle_count \
            FROM test_runs tr1 \
            LEFT JOIN test_case_runs tcr1 \
            ON tr1.run_id=tcr1.run_id \
            WHERE tcr1.case_run_status_id \
            NOT IN(1,4,5,6) \
            GROUP BY tr1.run_id \
            ORDER BY tr1.run_id \
        ) AS table1, ( \
            SELECT \
                tr2.run_id AS run_id, \
                count(tcr2.case_run_id) AS total_count \
            FROM test_runs tr2 \
            LEFT JOIN test_case_runs tcr2 \
            ON tr2.run_id=tcr2.run_id \
            GROUP BY tr2.run_id \
            ORDER BY tr2.run_id \
        ) AS table2 \
        WHERE table1.run_id=table2.run_id \
        AND table1.run_id=test_runs.run_id'
    
    total_num_caseruns = 'SELECT COUNT(*) \
        FROM test_case_runs \
        WHERE test_case_runs.run_id = test_runs.run_id'
    
    failed_case_run_percent = 'SELECT ROUND(no_idle_count/total_count*100,0) \
        FROM (\
            SELECT \
                tr1.run_id AS run_id, \
                count(tcr1.case_run_id) AS no_idle_count \
            FROM test_runs tr1 \
            LEFT JOIN test_case_runs tcr1 \
            ON tr1.run_id=tcr1.run_id \
            WHERE tcr1.case_run_status_id = 3 \
            GROUP BY tr1.run_id ORDER BY tr1.run_id\
        ) AS table1,( \
            SELECT \
                tr2.run_id AS run_id, \
                count(tcr2.case_run_id) AS total_count \
            FROM test_runs tr2 \
            LEFT JOIN test_case_runs tcr2 \
            ON tr2.run_id=tcr2.run_id \
            GROUP BY tr2.run_id \
            ORDER BY tr2.run_id\
        ) AS table2 \
        WHERE table1.run_id=table2.run_id \
        AND table1.run_id=test_runs.run_id'

    passed_case_run_percent = 'SELECT ROUND(no_idle_count/total_count*100,0) \
        FROM (\
            SELECT \
                tr1.run_id AS run_id, \
                count(tcr1.case_run_id) AS no_idle_count \
            FROM test_runs tr1 \
            LEFT JOIN test_case_runs tcr1 \
            ON tr1.run_id=tcr1.run_id \
            WHERE tcr1.case_run_status_id = 2\
            GROUP BY tr1.run_id ORDER BY tr1.run_id\
        ) AS table1,( \
            SELECT \
                tr2.run_id AS run_id, \
                count(tcr2.case_run_id) AS total_count \
            FROM test_runs tr2 \
            LEFT JOIN test_case_runs tcr2 \
            ON tr2.run_id=tcr2.run_id \
            GROUP BY tr2.run_id \
            ORDER BY tr2.run_id\
        ) AS table2 \
        WHERE table1.run_id=table2.run_id \
        AND table1.run_id=test_runs.run_id'

    total_num_review_cases = 'SELECT COUNT(*) FROM tcms_review_cases \
        WHERE tcms_reviews.id = tcms_review_cases.review_id'
    
    environment_group_for_run = 'SELECT GROUP_CONCAT(teg.name) \
        AS env_name FROM test_runs tr \
        LEFT JOIN tcms_env_plan_map tepm \
        ON tr.plan_id=tepm.plan_id \
        LEFT JOIN tcms_env_groups teg \
        ON tepm.group_id=teg.id \
        WHERE tr.run_id = test_runs.run_id \
        GROUP BY tr.run_id'

class ReportSQL(object):
    # Index
    index_product_plans_count = 'SELECT COUNT(plan_id) \
        FROM test_plans \
        WHERE test_plans.product_id = products.id'
    
    index_product_runs_count = 'SELECT COUNT(run_id) \
        FROM test_runs \
        INNER JOIN test_plans \
        ON test_runs.plan_id = test_plans.plan_id \
        WHERE test_plans.product_id = products.id'
    
    index_product_cases_count = 'SELECT COUNT(case_id) \
        FROM test_case_plans \
        INNER JOIN test_plans \
        ON test_case_plans.plan_id = test_plans.plan_id \
        WHERE test_plans.product_id = products.id'
    
    # Overview
    overview_runing_runs_count = 'SELECT \
        IF(tr.stop_date IS NULL, \'running\',\'finished\') AS status, \
        COUNT(tr.run_id) AS run_count \
        FROM test_runs tr \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        WHERE tps.product_id = %s \
        GROUP BY status'
    
    overview_case_runs_count = 'SELECT \
        tcrs.name AS test_case_status, COUNT(tcr.case_id) AS run_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        LEFT JOIN test_case_run_status tcrs \
        ON tcrs.case_run_status_id = tcr.case_run_status_id \
        WHERE tps.product_id = %s \
        GROUP BY tcrs.name \
        ORDER BY tcrs.sortkey'
    
    # Version
    version_plans_count = 'SELECT COUNT(plan_id) \
        FROM test_plans \
        WHERE test_plans.default_product_version = versions.value \
        AND test_plans.product_id = versions.product_id'
    
    version_running_runs_count = 'SELECT COUNT(run_id) \
        FROM test_runs \
        INNER JOIN test_plans \
        ON test_runs.plan_id = test_plans.plan_id \
        WHERE test_runs.stop_date IS NULL \
        AND test_plans.default_product_version = versions.value \
        AND test_plans.product_id = versions.product_id'
    
    version_finished_runs_count = 'SELECT COUNT(run_id) \
        FROM test_runs \
        INNER JOIN test_plans \
        ON test_runs.plan_id = test_plans.plan_id \
        WHERE test_runs.stop_date IS NOT NULL \
        AND test_plans.default_product_version = versions.value \
        AND test_plans.product_id = versions.product_id'
    
    version_cases_count = 'SELECT COUNT(case_id) \
        FROM test_case_plans \
        INNER JOIN test_plans \
        ON test_case_plans.plan_id = test_plans.plan_id \
        WHERE test_plans.default_product_version = versions.value \
        AND test_plans.product_id = versions.product_id'
    
    version_case_run_percent = 'SELECT ROUND(finished_count/total_count*100,0) AS finished_percentage FROM \
        (SELECT tps.product_id AS product_id, tps.default_product_version AS product_version, COUNT(tcr.case_id) AS total_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        GROUP BY tps.product_id,tps.default_product_version \
        ORDER BY tps.product_id,tps.default_product_version) AS t1 \
        LEFT JOIN \
        (SELECT tps.product_id AS product_id, tps.default_product_version AS product_version, COUNT(tcr.case_id) AS finished_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        WHERE tcr.case_run_status_id NOT IN (1,4,5,6) \
        GROUP BY tps.product_id,tps.default_product_version \
        ORDER BY tps.product_id,tps.default_product_version) AS t2 \
        ON t1.product_id = t2.product_id AND t1.product_version = t2.product_version \
        WHERE t1.product_id = versions.product_id AND t1.product_version = versions.value'
    
    version_failed_case_runs_count = 'SELECT COUNT(tcr.case_id) AS run_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        LEFT JOIN test_case_run_status tcrs ON tcrs.case_run_status_id = tcr.case_run_status_id \
        WHERE tps.product_id = versions.product_id AND tps.default_product_version = versions.value \
        AND tcrs.name = \'FAILED\' \
        GROUP BY tps.default_product_version \
        ORDER BY tps.default_product_version'
    
    version_case_runs_count = 'SELECT tcrs.name \
        AS test_case_status, COUNT(tcr.case_id) AS run_count \
        FROM test_case_run_status tcrs \
        LEFT JOIN test_case_runs tcr ON tcrs.case_run_status_id = tcr.case_run_status_id \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        WHERE tps.product_id = %s AND tps.default_product_version=%s \
        GROUP BY tcrs.name \
        ORDER BY tcrs.sortkey'
    
    # Build Zone
    build_total_runs = 'SELECT COUNT(DISTINCT run_id) \
        FROM test_runs \
        WHERE test_runs.build_id = test_builds.build_id'
    
    build_finished_runs = 'SELECT COUNT(DISTINCT tr2.run_id) \
        FROM test_runs tr2 \
        WHERE tr2.build_id = test_builds.build_id \
        AND tr2.stop_date IS NOT NULL'
    
    build_finished_case_runs_percent = 'SELECT ROUND(finished_count/total_count*100,0) \
        AS finished_percentage FROM \
        (SELECT tps.product_id AS product_id, tr.build_id AS tr_build_id, COUNT(tcr.case_id) AS total_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id  \
        GROUP BY tps.product_id,tr.build_id \
        ORDER BY tps.product_id,tr.build_id) AS t1 \
        LEFT JOIN \
        (SELECT tps.product_id AS product_id, tr.build_id AS tr_build_id, COUNT(tcr.case_id) AS finished_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        WHERE tcr.case_run_status_id NOT IN (1,4,5,6) \
        GROUP BY tps.product_id,tr.build_id \
        ORDER BY tps.product_id,tr.build_id) AS t2 \
        ON t1.product_id = t2.product_id AND t1.tr_build_id = t2.tr_build_id \
        WHERE t1.product_id = test_builds.product_id AND t1.tr_build_id = test_builds.build_id'
    
    build_failed_case_run_count = 'SELECT COUNT(tcr.case_id) AS run_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        LEFT JOIN test_case_run_status tcrs ON tcrs.case_run_status_id = tcr.case_run_status_id \
        WHERE tps.product_id = test_builds.product_id AND tr.build_id = test_builds.build_id \
        AND tcrs.name = \'FAILED\' \
        GROUP BY tr.build_id \
        ORDER BY tr.build_id'
    
    build_runs_percent = 'SELECT ROUND(finished_count/total_count*100,0) \
        AS finished_percentage FROM \
        (SELECT trs.build_id AS build_id, COUNT(tcr.case_id) AS total_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs trs ON tcr.run_id = trs.run_id \
        GROUP BY trs.summary) AS t1 \
        LEFT JOIN \
        (SELECT trs.build_id AS build_id, COUNT(tcr.case_id) AS finished_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs trs ON tcr.run_id = trs.run_id \
        WHERE trs.stop_date IS NOT NULL \
        GROUP BY trs.summary) AS t2 \
        WHERE t1.build_id = t2.build_id AND t1.build_id = test_builds.build_id'
    
    build_case_runs_count = 'SELECT tcrs.name \
        AS test_case_status, COUNT(tcr.case_id) AS run_count \
        FROM test_case_run_status tcrs          \
        LEFT JOIN test_case_runs tcr ON tcrs.case_run_status_id = tcr.case_run_status_id \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        WHERE tr.build_id = %s \
        GROUP BY tcrs.name \
        ORDER BY tcrs.sortkey;'
    
    # Component Zone
    component_total_cases = 'SELECT COUNT(DISTINCT tcc1.case_id) \
        FROM test_case_components tcc1 \
        WHERE tcc1.component_id=components.id'
    
    component_finished_case_run_percent = 'SELECT ROUND(finished_count/total_count*100,0) \
        AS finished_percentage FROM \
        (SELECT tps.product_id AS product_id, tcc.component_id AS tcc_component_id, COUNT(tcr.case_id) AS total_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        LEFT JOIN test_case_components tcc ON tcr.case_id=tcc.case_id \
        GROUP BY tps.product_id,tcc.component_id \
        ORDER BY tps.product_id,tcc.component_id) AS t1 \
        LEFT JOIN \
        (SELECT tps.product_id AS product_id, tcc.component_id AS tcc_component_id, COUNT(tcr.case_id) AS finished_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        LEFT JOIN test_case_components tcc ON tcr.case_id=tcc.case_id \
        WHERE tcr.case_run_status_id NOT IN (1,4,5,6) \
        GROUP BY tps.product_id,tcc.component_id \
        ORDER BY tps.product_id,tcc.component_id) AS t2 \
        ON t1.product_id = t2.product_id AND t1.tcc_component_id = t2.tcc_component_id \
        WHERE t1.product_id = components.product_id AND t1.tcc_component_id = components.id'
    
    component_failed_case_run_count = 'SELECT COUNT(tcr.case_id) AS run_count \
        FROM test_case_runs tcr \
        LEFT JOIN test_runs tr ON tcr.run_id = tr.run_id \
        LEFT JOIN test_plans tps ON tr.plan_id = tps.plan_id \
        LEFT JOIN test_case_run_status tcrs ON tcrs.case_run_status_id = tcr.case_run_status_id \
        LEFT JOIN test_case_components tcc ON tcr.case_id=tcc.case_id \
        WHERE tps.product_id = components.product_id AND tcc.component_id = components.id \
        AND tcrs.name = \'FAILED\' \
        GROUP BY tcc.component_id \
        ORDER BY tcc.component_id'
    
    component_case_runs_count = 'SELECT tcrs.name \
        AS test_case_status, COUNT(tcr.case_id) AS run_count \
        FROM test_case_run_status tcrs \
        LEFT JOIN test_case_runs tcr ON tcrs.case_run_status_id = tcr.case_run_status_id \
        LEFT JOIN test_case_components tcs ON tcr.case_id = tcs.case_id \
        LEFT JOIN components com ON tcs.component_id = com.id \
        WHERE com.id = %s \
        GROUP BY tcrs.name \
        ORDER BY tcrs.sortkey'
    
    # Custom Search Zone
    custom_search_plans_count = 'SELECT COUNT(DISTINCT tps.plan_id) \
        FROM test_plans tps \
        LEFT JOIN test_runs trs ON tps.plan_id = trs.plan_id \
        LEFT JOIN test_builds tbs ON trs.build_id = tbs.build_id \
        WHERE trs.build_id = test_builds.build_id AND tps.plan_id = trs.plan_id \
        GROUP BY tbs.build_id'
    
    custom_search_runs_count = 'SELECT COUNT(DISTINCT run_id) \
        FROM test_runs \
        WHERE test_runs.build_id = test_builds.build_id'
    
    custom_search_case_runs_count = 'SELECT COUNT(DISTINCT case_run_id) \
        FROM test_case_runs \
        WHERE test_case_runs.build_id = test_builds.build_id'

    # added by zheliu
    custom_search_case_runs_count_under_run = 'SELECT COUNT(DISTINCT tcrs.case_run_id) \
        FROM test_case_runs tcrs \
        LEFT JOIN test_runs trs ON tcrs.run_id = trs.run_id \
        LEFT JOIN test_builds tbs ON trs.build_id = tbs.build_id \
        WHERE trs.build_id = test_builds.build_id AND tcrs.run_id = trs.run_id \
        GROUP BY tbs.build_id'

    custom_search_case_runs_count_by_status_under_run = 'SELECT COUNT(DISTINCT tcrs.case_run_id) \
        FROM test_case_runs tcrs \
        LEFT JOIN test_runs trs ON tcrs.run_id = trs.run_id \
        LEFT JOIN test_builds tbs ON trs.build_id = tbs.build_id \
        WHERE trs.build_id = test_builds.build_id \
        AND tcrs.run_id = trs.run_id \
        AND tcrs.case_run_status_id = %s'
    
    custom_search_case_runs_count_by_status = 'SELECT COUNT(DISTINCT case_run_id) \
        FROM test_case_runs \
        WHERE test_case_runs.build_id = test_builds.build_id AND test_case_runs.case_run_status_id = %s'

    # added by chaobin
    case_runs_count_by_status_under_run = 'SELECT COUNT(DISTINCT case_run_id) \
        FROM test_case_runs \
        WHERE test_case_runs.run_id = test_runs.run_id AND test_case_runs.case_run_status_id = %s'

    custom_details_case_run_count = 'SELECT tcrs.name \
        AS test_case_status, COUNT(tcr.case_id) AS case_run_count \
        FROM test_case_run_status tcrs          \
        LEFT JOIN test_case_runs tcr ON tcrs.case_run_status_id = tcr.case_run_status_id \
        WHERE tcr.run_id = %s \
        GROUP BY tcrs.name \
        ORDER BY tcrs.sortkey'
