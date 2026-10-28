import request from '@/utils/request'

export const fileService = {
  // 文件上传
  uploadFile: async (data, id, type) => {
    try {
      const params = type === 'requirement' ? { requirement_id: id } : { resource_id: id }
      const response = await request.post(`/api/v1/project/virtual-files/upload_file/`, data, {
        params: params,
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '文件上传失败' }
    }
  },

  // 文件删除
  deleteFile: async (data, id, type) => {
    try {
      const params = type === 'requirement' ? { requirement_id: id } : { resource_id: id }
      const response = await request.delete(`/api/v1/project/virtual-files/file_delete/`, {
        data: data,
        params: params,
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '文件删除失败' }
    }
  }
}
