// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 自动隐藏提示消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5秒后自动关闭
    });

    // 为标签添加点击事件，用于筛选
    const tagLinks = document.querySelectorAll('[href^="/?tag_id="], [href="/"]');
    tagLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // 可以在这里添加加载指示器
            const loadingIndicator = document.createElement('div');
            loadingIndicator.className = 'position-fixed top-50 left-50 transform -translate-x-1/2 -translate-y-1/2 bg-white p-4 rounded shadow';
            loadingIndicator.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
            document.body.appendChild(loadingIndicator);
        });
    });
});
