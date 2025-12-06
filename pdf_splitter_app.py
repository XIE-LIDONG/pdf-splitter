
import streamlit as st
import PyPDF2
import zipfile
import io

# 页面设置
st.set_page_config(page_title="PDF分割器", page_icon="📄")

# 标题
st.title("📄 PDF分割器")
st.write("上传PDF，设置页数，自动分割")

# 1. 文件上传
uploaded_file = st.file_uploader("选择PDF文件", type="pdf")

if uploaded_file:
    # 显示文件信息
    file_size = len(uploaded_file.getvalue()) / 1024 / 1024
    st.success(f"✅ 已选择: {uploaded_file.name} ({file_size:.1f} MB)")
    
    # 2. 设置页数
    pages = st.number_input("每份多少页", min_value=1, max_value=100, value=15)
    
    # 3. 开始按钮
    if st.button("开始分割", type="primary"):
        with st.spinner("正在处理..."):
            try:
                # 读取PDF
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                total_pages = len(pdf_reader.pages)
                st.info(f"📄 总页数: {total_pages}")
                
                # 计算分割数量
                num_files = (total_pages + pages - 1) // pages
                
                # 创建ZIP文件
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    # 进度条
                    progress_bar = st.progress(0)
                    
                    for i in range(num_files):
                        # 计算页码范围
                        start = i * pages
                        end = min((i + 1) * pages, total_pages)
                        
                        # 创建新PDF
                        pdf_writer = PyPDF2.PdfWriter()
                        for page_num in range(start, end):
                            pdf_writer.add_page(pdf_reader.pages[page_num])
                        
                        # 生成文件名
                        filename = f"part_{i+1:02d}_p{start+1:03d}-{end:03d}.pdf"
                        
                        # 保存到内存
                        pdf_data = io.BytesIO()
                        pdf_writer.write(pdf_data)
                        pdf_data.seek(0)
                        
                        # 添加到ZIP
                        zip_file.writestr(filename, pdf_data.getvalue())
                        
                        # 更新进度
                        progress_bar.progress((i + 1) / num_files)
                
                # 完成
                st.success(f"✅ 分割完成！共 {num_files} 个文件")
                
                # 4. 下载按钮
                zip_buffer.seek(0)
                st.download_button(
                    label="📥 下载所有文件 (ZIP)",
                    data=zip_buffer,
                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_分割结果.zip",
                    mime="application/zip"
                )
                
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")
else:
    st.info("请先上传PDF文件")
