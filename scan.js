document.getElementById('start-scan').addEventListener('click', function() {
    // Start the scan and update progress
    fetch('/scan', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.message === "Scan started!") {
                updateProgress();
            }
        });
});

function updateProgress() {
    const interval = setInterval(function() {
        fetch('/progress')
            .then(response => response.json())
            .then(data => {
                document.getElementById('progress').style.width = data.progress + '%';

                if (data.progress >= 100) {
                    clearInterval(interval);
                    document.getElementById('scan-result').textContent = 'Scan Complete';
                }
            });
    }, 1000);
}
