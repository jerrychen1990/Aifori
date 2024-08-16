import streamlit as st
import streamlit.components.v1 as components

# 定义 HTML 和 JavaScript 代码
html_code = """
<!DOCTYPE html>
<html>
<head>
    <script>
        function showAlert() {
            alert("Hello from JavaScript!");
        }

        function updateContent(content) {
            document.getElementById('content').innerText = content;
        }
    </script>
</head>
<body>
    <button onclick="showAlert()">Show Alert</button>
    <button onclick="updateContent('Updated from JavaScript!')">Update Content</button>
    <div id="content">Initial Content</div>
</body>
</html>
"""

# 嵌入 HTML 和 JavaScript
components.html(html_code, height=300)

# 在 Streamlit 应用中添加按钮来触发 JavaScript 函数
if st.button("Trigger JS Function"):
    st.components.v1.html("""
    <script>
        // 通过 JavaScript 调用函数
        // document.querySelector('button').click();  // 触发第一个按钮的点击事件
                          showAlert();
    </script>
    """, height=0)
