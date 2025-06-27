if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {
    update_toast: function(toastData, closeClicks) {
        // Get the current context
        const ctx = window.dash_clientside.callback_context;
        
        // Default class (hidden toast)
        let className = "fixed top-4 right-4 z-50 transition-opacity duration-300 opacity-0 pointer-events-none";
        let message = "";
        
        // If toast data changed and there's a message
        if (ctx && ctx.triggered && ctx.triggered[0].prop_id === 'toast-data.data' && toastData && toastData.message) {
            // Show the toast
            className = "fixed top-4 right-4 z-50 transition-opacity duration-300 opacity-100";
            message = toastData.message;
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                const toastContainer = document.getElementById('toast-container');
                if (toastContainer) {
                    toastContainer.className = "fixed top-4 right-4 z-50 transition-opacity duration-300 opacity-0 pointer-events-none";
                }
            }, 5000);
        }
        
        // If close button was clicked
        if (ctx && ctx.triggered && ctx.triggered[0].prop_id === 'toast-close.n_clicks' && closeClicks > 0) {
            className = "fixed top-4 right-4 z-50 transition-opacity duration-300 opacity-0 pointer-events-none";
        }
        
        return [className, message];
    }
};