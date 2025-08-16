# 📄 File Upload and AI Analysis Feature

Tính năng upload file và phân tích bằng AI đã được thêm vào EmbeddedChat, cho phép bạn upload các loại file khác nhau và để AI phân tích chúng.

## 🚀 Tính năng chính

### 📁 Loại file được hỗ trợ

**Hình ảnh:**
- JPEG, JPG, PNG, GIF, WebP, BMP, TIFF
- AI có thể mô tả nội dung, trích xuất text, phân tích hình ảnh

**Tài liệu:**
- PDF (với text extraction)
- Microsoft Word (.docx)
- Plain text (.txt)
- Markdown (.md)

**Dữ liệu:**
- CSV files
- JSON files
- Excel files (.xlsx)

### 🤖 AI Analysis

- **OpenAI GPT-4o Vision**: Phân tích hình ảnh chi tiết, mô tả đối tượng, trích xuất text
- **Claude Vision**: Phân tích hình ảnh với khả năng hiểu ngữ cảnh cao
- **Text Analysis**: Tóm tắt, phân tích nội dung cho tất cả loại tài liệu

## 🎯 Cách sử dụng

### Frontend (Web Interface)

1. **Mở Document Panel**: Click vào icon documents trong chat header
2. **Upload File**: 
   - Drag & drop file vào drop zone
   - Hoặc click "Click to upload"
   - Chọn AI provider và API key để phân tích tự động
3. **View Documents**: Xem danh sách files đã upload
4. **Chat with Documents**: Click vào document để thêm vào chat context

### Backend API

#### Upload File
```bash
POST /api/v1/documents/upload
Content-Type: multipart/form-data

# Form fields:
- file: (file) The file to upload
- ai_provider: (string, optional) "openai" or "claude"  
- api_key: (string, optional) API key for AI analysis
```

#### Get Document Content  
```bash
GET /api/v1/documents/{document_id}/content
```

#### Analyze Document
```bash
POST /api/v1/documents/{document_id}/analyze
Content-Type: multipart/form-data

# Form fields:
- ai_provider: (string) "openai" or "claude"
- api_key: (string) API key for AI provider
```

#### Chat with Documents
```bash
POST /api/v1/chat/send
Content-Type: application/json

{
  "message": "Analyze this document",
  "provider": "openai",
  "model": "gpt-4o",
  "apiKey": "your-api-key",
  "attachedDocuments": [1, 2, 3]  // Document IDs
  // ... other chat parameters
}
```

## 🛠️ Setup

### Backend Dependencies

```bash
cd backend
pip install -r requirements_file_analysis.txt
```

Hoặc cài đặt từng package:

```bash
pip install PyPDF2 PyMuPDF Pillow python-docx openpyxl openai anthropic google-generativeai
```

### Database Migration

File upload sử dụng bảng `documents` có sẵn. Không cần migration thêm.

### File Storage

Files được lưu trong thư mục `backend/uploads/`. Đảm bảo thư mục này có quyền write.

## 🧪 Testing

### Manual Testing

1. **Start Backend**:
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

2. **Start Frontend**:
```bash
cd frontend  
npm run dev
```

3. **Test Upload**: Upload một file PDF hoặc hình ảnh
4. **Test Analysis**: Thử phân tích với AI
5. **Test Chat**: Gửi message với document đính kèm

### Automated Testing

```bash
cd backend
python test_file_upload.py
```

*Nhớ cập nhật API key trong test script trước khi chạy.*

## 📊 API Response Examples

### Upload Response
```json
{
  "id": 1,
  "filename": "abc123.pdf",
  "original_filename": "document.pdf", 
  "file_size": 1024000,
  "mime_type": "application/pdf",
  "status": "ready",
  "extracted_text": "Document content...",
  "summary": "AI generated summary...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Chat with Documents Response
```json
{
  "content": "Based on the attached document, I can see that...",
  "usage": {
    "promptTokens": 1500,
    "completionTokens": 300,
    "totalTokens": 1800
  },
  "metadata": {
    "provider": "openai",
    "model": "gpt-4o"
  }
}
```

## 🔧 Configuration

### File Limits

```python
# In backend/src/api/routes/documents.py
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### Supported MIME Types

```python
ALLOWED_MIME_TYPES = {
    "text/plain", "text/markdown", 
    "application/pdf", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg", "image/jpg", "image/png", "image/gif",
    "image/webp", "image/bmp", "image/tiff",
    "text/csv", "application/json",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
}
```

## 🚨 Lưu ý quan trọng

1. **API Keys**: Cần API key hợp lệ cho OpenAI hoặc Claude để sử dụng AI analysis
2. **File Size**: Giới hạn 50MB per file
3. **Security**: Đảm bảo validate file types để tránh security risks
4. **Storage**: Files được lưu trên disk, cân nhắc cloud storage cho production
5. **Performance**: Large files có thể mất thời gian để process

## 🔮 Tính năng tương lai

- [ ] Cloud storage integration (AWS S3, Google Cloud)
- [ ] Batch file processing
- [ ] OCR cho hình ảnh có text
- [ ] Video/Audio analysis
- [ ] Document comparison
- [ ] Advanced search trong documents
- [ ] File versioning
- [ ] Collaborative annotation

## 🐛 Troubleshooting

### Common Issues

1. **"File type not supported"**
   - Kiểm tra MIME type trong `ALLOWED_MIME_TYPES`
   - Đảm bảo file không corrupted

2. **"AI analysis failed"**
   - Kiểm tra API key hợp lệ
   - Kiểm tra network connection
   - Xem logs chi tiết trong console

3. **"Document not found"**
   - Kiểm tra document ID
   - Đảm bảo user có quyền truy cập

4. **Upload slow/timeout**
   - Kiểm tra file size
   - Kiểm tra network connection
   - Tăng timeout trong frontend

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
python -m uvicorn main:app --reload --log-level debug
```

## 📞 Support

Nếu gặp vấn đề, hãy:
1. Kiểm tra logs trong browser console và backend logs
2. Thử test với file nhỏ trước
3. Đảm bảo tất cả dependencies đã được cài đặt
4. Kiểm tra API keys và network connection
