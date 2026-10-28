import request from '@/utils/request'

/**
 * 获取成果列表
 * @param {number|string} projectId
 * @param {Object} params { page, page_size, milestone, include_deprecated, stage_type, latest_per_stage }
 */
export function getDeliverables(projectId, params = {}) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/deliverables/`,
    method: 'get',
    params
  })
}

/**
 * 获取成果详情
 * @param {number|string} projectId
 * @param {number|string} deliverableId
 */
export function getDeliverableDetail(projectId, deliverableId) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/deliverables/${deliverableId}/`,
    method: 'get'
  })
}

/**
 * 提交成果（multipart/form-data）
 * 注意：不要手动设置 Content-Type，交给浏览器/axios 根据 FormData 自动加入 boundary
 * @param {number|string} projectId
 * @param {FormData} formData
 *  需要的字段：
 *  - title(必填)
 *  - stage_type(必填: early/middle/final)
 *  - is_milestone('true'|'false')
 *  - description, progress_description, notes
 *  - uploaded_files(可多文件)
 *  - cloud_links, cloud_password
 *  - virtual_folder_path
 */
export function submitDeliverable(projectId, formData) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/deliverables/submit/`,
    method: 'post',
    data: formData
    // 切勿手动设置 headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 更新成果（multipart/form-data）
 * 注意：不要手动设置 Content-Type，交给浏览器/axios 根据 FormData 自动加入 boundary
 * @param {number|string} projectId
 * @param {number|string} deliverableId
 * @param {FormData} formData
 *  可选字段：title、description、progress_description、notes、cloud_links、cloud_password、is_deprecated
 */
export function updateDeliverable(projectId, deliverableId, formData) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/deliverables/${deliverableId}/update/`,
    method: 'put',
    data: formData
    // 切勿手动设置 headers: { 'Content-Type': 'multipart/form-data' }
  })
}
