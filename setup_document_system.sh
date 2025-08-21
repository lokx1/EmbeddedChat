#!/bin/bash

echo "🚀 Setting up Modern Document Processing System..."

# Backend setup
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements_documents.txt

# Frontend setup  
echo "🎨 Installing Node.js dependencies..."
cd ../frontend
npm install react-pdf pdfjs-dist @react-pdf-viewer/core @react-pdf-viewer/default-layout mammoth docx-preview react-dropzone react-beautiful-dnd lucide-react

echo "✅ Document system setup complete!"
echo ""
echo "🔧 Supported formats:"
echo "  📄 Documents: PDF, DOCX, DOC, PPT, PPTX, RTF, ODT, ODP"
echo "  📝 Text: TXT, MD, LaTeX, TEX, CSV, JSON"
echo "  🖼️  Images: JPG, PNG, GIF, WebP, BMP, TIFF"
echo "  🎬 Media: MP4, MOV, AVI, WebM, MP3, WAV, AAC"
echo ""
echo "🤖 AI Features:"
echo "  ✨ Automatic content extraction"
echo "  📊 Document summarization"
echo "  🔍 Intelligent search"
echo "  💬 Q&A with documents"
echo ""
echo "🎯 Ready to process documents with modern AI capabilities!"
