import streamlit as st
import PyPDF2
import zipfile
import io

# Page configuration
st.set_page_config(page_title="PDF Splitter", page_icon="📄")

# Title + Signature (same line, signature top-right small font)
st.markdown(
    """
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <h1 style='margin: 0;'>📄 PDF Splitter</h1>
        <p style='color: #666666; font-size: 14px; margin: 0;'>By XIE LI DONG</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Description
st.write("Upload a PDF file, set page count per split file, and split automatically")

# 1. File upload
uploaded_file = st.file_uploader("Select PDF File", type="pdf")

if uploaded_file:
    # Show file info
    file_size = len(uploaded_file.getvalue()) / 1024 / 1024
    st.success(f"✅ Selected: {uploaded_file.name} ({file_size:.1f} MB)")
    
    # 2. Set page count
    pages = st.number_input("Pages per split file", min_value=1, max_value=100, value=15)
    
    # 3. Start button
    if st.button("Start Splitting", type="primary"):
        with st.spinner("Processing..."):
            try:
                # Read PDF
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                total_pages = len(pdf_reader.pages)
                st.info(f"📄 Total Pages: {total_pages}")
                
                # Calculate number of split files
                num_files = (total_pages + pages - 1) // pages
                
                # Create ZIP file
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    # Progress bar
                    progress_bar = st.progress(0)
                    
                    for i in range(num_files):
                        # Calculate page range
                        start = i * pages
                        end = min((i + 1) * pages, total_pages)
                        
                        # Create new PDF
                        pdf_writer = PyPDF2.PdfWriter()
                        for page_num in range(start, end):
                            pdf_writer.add_page(pdf_reader.pages[page_num])
                        
                        # Generate filename
                        filename = f"part_{i+1:02d}_p{start+1:03d}-{end:03d}.pdf"
                        
                        # Save to memory
                        pdf_data = io.BytesIO()
                        pdf_writer.write(pdf_data)
                        pdf_data.seek(0)
                        
                        # Add to ZIP
                        zip_file.writestr(filename, pdf_data.getvalue())
                        
                        # Update progress
                        progress_bar.progress((i + 1) / num_files)
                
                # Completion
                st.success(f"✅ Splitting Completed! Total {num_files} files generated")
                
                # 4. Download button
                zip_buffer.seek(0)
                st.download_button(
                    label="📥 Download All Files (ZIP)",
                    data=zip_buffer,
                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_split_results.zip",
                    mime="application/zip"
                )
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
else:
    st.info("Please upload a PDF file first")
