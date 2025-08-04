# 📧 Email Report Service - Comprehensive Documentation

## 🎯 Overview

Hệ thống Email Report Service được thiết kế để gửi các báo cáo comprehensive về logs và events của workflow executions. Service này tạo ra các báo cáo chuyên nghiệp với analytics charts và detailed data.

## 🌟 Key Features

### 📊 Workflow Execution Reports
- **Comprehensive Analysis**: Phân tích chi tiết về workflow success/failure
- **Visual Analytics**: Charts tự động về success rates và performance metrics
- **Timeline Execution**: Timeline chi tiết của từng bước thực thi
- **Error Breakdown**: Phân loại và phân tích lỗi chi tiết
- **Professional Format**: HTML emails với formatting chuyên nghiệp

### 📈 Daily Analytics Reports  
- **Performance Dashboard**: Tổng quan performance của tất cả workflows trong ngày
- **Trend Analysis**: Phân tích xu hướng theo giờ và thời gian
- **Error Statistics**: Thống kê lỗi chi tiết theo loại
- **Top Workflows**: Ranking workflows theo performance
- **Historical Comparison**: So sánh với các ngày trước

## 🏗️ Architecture

```
📧 Email Report Service
├── 🔧 Backend Services
│   ├── EmailReportService (Core service)
│   ├── EmailService (SMTP integration)
│   └── API Endpoints (REST APIs)
├── 🎨 Frontend Components
│   ├── EmailReportPanel (UI for sending reports)
│   └── Enhanced Execution Panel (Integration)
└── 📊 Data Processing
    ├── Analytics Chart Generation
    ├── Log Processing
    └── Event Aggregation
```

## 🚀 Quick Start

### 1. Cấu hình SMTP Settings

Thêm vào file `.env`:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 2. Install Dependencies

```bash
# Backend dependencies (đã có sẵn)
pip install matplotlib pandas

# Frontend dependencies (đã có sẵn)
# Không cần install thêm gì
```

### 3. Start Services

```bash
# Backend
cd backend
python -m uvicorn src.main:app --reload

# Frontend  
cd frontend
npm start
```

## 📖 Usage Guide

### 🖥️ Frontend Usage

1. **Execute a workflow** trong Workflow Editor
2. **Mở Execution Panel** để xem execution details
3. **Click nút "📧 Email Report"** 
4. **Chọn report type**:
   - **Execution Report**: Chi tiết về workflow execution cụ thể
   - **Daily Analytics**: Tổng quan performance trong ngày
5. **Nhập email** và click "Send Report"

### 🔧 API Usage

#### Send Workflow Execution Report

```bash
POST /api/v1/workflow/instances/{instance_id}/send-report
Content-Type: application/json

{
  "recipient_email": "admin@company.com",
  "include_analytics": true,
  "include_detailed_logs": true
}
```

#### Send Daily Analytics Report

```bash
POST /api/v1/workflow/reports/daily-analytics
Content-Type: application/json

{
  "recipient_email": "manager@company.com", 
  "date": "2025-08-04"
}
```

## 📊 Report Structure

### 📧 Execution Report Content

```
📊 Workflow Execution Report
├── 📈 Summary Metrics
│   ├── Success Rate (visual chart)
│   ├── Execution Duration
│   ├── Steps Completed/Failed
│   └── Error Count
├── ℹ️ Execution Details
│   ├── Instance ID
│   ├── Start/End Times
│   ├── Workflow Name
│   └── Status Information
├── 📈 Execution Timeline
│   ├── Step-by-step progress
│   ├── Timestamps
│   └── Duration per step
├── 🔴 Error Summary
│   ├── Error messages
│   ├── Timestamps
│   └── Resolution status
├── 📋 Detailed Logs
│   ├── Full execution logs
│   ├── Node-level details
│   └── Performance metrics
└── 📎 Attachments
    ├── Analytics chart (PNG)
    └── Raw data (JSON)
```

### 📈 Daily Analytics Report Content

```
📊 Daily Analytics Report
├── 📈 Performance Metrics
│   ├── Total Executions
│   ├── Success/Failure Rates
│   ├── Average Duration
│   └── Trend Charts
├── 🔍 Error Breakdown
│   ├── Error types và counts
│   ├── Most common errors
│   └── Resolution rates
├── 📋 Recent Executions
│   ├── Top workflows
│   ├── Performance comparison
│   └── Status overview
└── 📊 Visual Charts
    ├── Success rate trends
    ├── Performance over time
    └── Error distribution
```

## 🔧 Technical Implementation

### Core Components

#### 1. EmailReportService
```python
class EmailReportService:
    async def send_workflow_completion_report(...)
    async def send_daily_analytics_report(...)
    async def _generate_analytics_chart(...)
    async def _generate_report_html(...)
```

#### 2. Data Models
```python
@dataclass
class WorkflowExecutionSummary:
    workflow_name: str
    instance_id: str
    status: str
    success_rate: float
    # ... more fields

@dataclass  
class WorkflowAnalytics:
    total_executions: int
    success_rate_percentage: float
    error_breakdown: Dict[str, int]
    # ... more fields
```

#### 3. Chart Generation
- **Matplotlib Integration**: Tự động tạo charts
- **Multiple Chart Types**: Pie charts, bar charts, line charts
- **Professional Styling**: Color schemes và formatting
- **PNG Export**: High-quality image attachments

## 📚 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workflow/instances/{id}/send-report` | Send execution report |
| POST | `/workflow/reports/daily-analytics` | Send daily report |

### Response Format

```json
{
  "success": true,
  "message": "Report sent successfully",
  "recipient_email": "user@example.com",
  "instance_id": "abc123...",
  "attachments_count": 2
}
```

## 🎨 Customization

### Email Template Customization

1. **HTML Templates**: Modify `_generate_report_html()` method
2. **Chart Styles**: Customize matplotlib styling  
3. **Color Schemes**: Update CSS trong HTML templates
4. **Content Sections**: Add/remove sections trong report structure

### Chart Customization

```python
# Example: Custom chart styling
fig.suptitle('Custom Title', fontsize=16, fontweight='bold')
ax.set_facecolor('#f8fafc')
plt.style.use('seaborn-v0_8')  # Professional styling
```

## 🔍 Troubleshooting

### Common Issues

1. **SMTP Authentication Errors**
   ```
   Solution: Check SMTP credentials và enable "App Passwords" for Gmail
   ```

2. **Chart Generation Errors**
   ```
   Solution: Install matplotlib và set non-interactive backend
   ```

3. **Email Formatting Issues**
   ```
   Solution: Test với different email clients và adjust HTML
   ```

4. **Large Attachment Errors**
   ```
   Solution: Implement compression cho JSON attachments
   ```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Considerations

- **Background Processing**: All email sending via background tasks
- **Chart Caching**: Consider caching charts for similar data
- **Data Pagination**: Limit log entries in reports
- **Attachment Size**: Monitor JSON file sizes

## 🔮 Future Enhancements

### Planned Features

1. **📊 Advanced Analytics**
   - More chart types
   - Interactive charts
   - Comparative analysis

2. **🎨 Template Engine**
   - Customizable templates
   - Brand-specific styling
   - Multiple layouts

3. **📱 Multi-channel Delivery**
   - Slack integration
   - Microsoft Teams
   - SMS notifications

4. **🔄 Scheduled Reports**
   - Weekly/monthly reports
   - Automatic scheduling
   - Report subscriptions

## 📞 Support

### Getting Help

1. **Documentation**: Check this README và inline comments
2. **Debug Logs**: Enable debug mode for detailed logging
3. **API Testing**: Use test scripts trong repository
4. **Frontend Testing**: Use browser developer tools

### Test Scripts

```bash
# Test email service
python test_email_report_service.py

# Demo full system
python demo_email_report_system.py
```

## 🎯 Best Practices

1. **Email Configuration**:
   - Use app-specific passwords
   - Test với different email providers
   - Configure appropriate timeouts

2. **Report Content**:
   - Keep HTML emails under 100KB
   - Optimize images for email clients
   - Include plain text fallbacks

3. **Performance**:
   - Use background tasks for sending
   - Implement proper error handling
   - Monitor email delivery rates

4. **Security**:
   - Validate email addresses
   - Sanitize user inputs
   - Use secure SMTP connections

---

## 🎉 Summary

Email Report Service cung cấp comprehensive solution để gửi detailed workflow reports với:

- ✅ **Professional HTML emails** với embedded charts
- ✅ **Comprehensive analytics** về workflow performance  
- ✅ **Detailed error analysis** và troubleshooting info
- ✅ **User-friendly UI** integration
- ✅ **Flexible API** cho automation
- ✅ **Rich attachments** với raw data

Perfect cho monitoring, debugging, và reporting workflow performance! 🚀
