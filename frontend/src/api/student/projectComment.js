import request from '@/utils/request'

// 获取评语列表（项目级或成果级）
// params: { page=1, page_size=10, deliverable_id }
export function getProjectComments(projectId, params = {}) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/comments/`,
    method: 'get',
    params
  })
}

// 获取某条评语的回复列表
// params: { page=1, page_size=10 }
export function getCommentReplies(projectId, commentId, params = {}) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/comments/${commentId}/replies/`,
    method: 'get',
    params
  })
}

// 发布评语或回复评语
// query: { deliverable_id, parent_comment_id } （deliverable_id 必填；parent_comment_id 为空时为“主动留言”，有值时为“回复某条评语”）
// body: { content }
export function postProjectComment(projectId, body = { content: '' }, query = {}) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/comments/create/`,
    method: 'post',
    params: query,
    data: body
  })
}
