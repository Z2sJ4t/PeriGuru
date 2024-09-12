"""
   Copyright [2021] [UIED mulong.xie@anu.edu.au]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

def recog_repetition_elements(compos, show=False):
    '''
    produced dataframe attributes: 'alignment', 'group'
    '''
    compos_cp = compos.copy()

    # step1. cluster compos
    compos_cp.cluster_dbscan_by_attr('center_column', eps=15, show=show)
    compos_cp.cluster_dbscan_by_attr('center_row', eps=15, show=show)
    # compos_cp.cluster_dbscan_by_attr('area', eps=500, show=show)
    compos_cp.cluster_area_by_relational_size(show=show)

    # step2. group compos according to clustering
    compos_cp.group_by_clusters(cluster='cluster_center_column', alignment='v', show=show)
    compos_cp.check_group_of_two_compos_validity_by_areas(show=show)

    compos_cp.regroup_compos_by_compos_gap(numbered_group=True)
    compos_cp.check_group_validity_by_compos_gap(show=show, numbered_group=True)

    compos_cp.group_by_clusters_conflict(cluster='cluster_center_row', alignment='h', show=show)
    compos_cp.check_group_of_two_compos_validity_by_areas(show=show)

    return compos_cp.dataframe

def recog_repetition_texts(compos, show=False):
    compos_cp = compos.copy()

    # step1. cluster compos
    compos_cp.cluster_dbscan_by_attr('row_min', eps=10, show=show)
    compos_cp.check_group_by_attr(target_attr='cluster_row_min', check_by='height', eps=15, show=show)
    compos_cp.cluster_dbscan_by_attr('column_min', eps=15, show=show)
    compos_cp.check_group_by_attr(target_attr='cluster_column_min', check_by='height', eps=30, show=show)

    # step2. group compos according to clustering
    compos_cp.group_by_clusters('cluster_row_min', alignment='h', show=show)
    compos_cp.check_group_of_two_compos_validity_by_areas(show=show)

    compos_cp.regroup_compos_by_compos_gap(numbered_group=True)
    compos_cp.check_group_validity_by_compos_gap(show=show, numbered_group=True)

    compos_cp.group_by_clusters_conflict('cluster_column_min', alignment='v', show=show)
    compos_cp.check_group_of_two_compos_validity_by_areas(show=show)
    compos_cp.regroup_left_compos_by_cluster('cluster_column_min', alignment='v', show=show)

    return compos_cp.dataframe