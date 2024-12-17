$(document).ready(function() {
    $('#start-scan').click(function() {
        // Start the scan
        $.post('/scan', function(response) {
            $('#scan-status').text(response.message);

            // Continuously check for progress
            let interval = setInterval(function() {
                $.get('/progress', function(progressResponse) {
                    let progress = progressResponse.progress;
                    let detectedFiles = progressResponse.detected_files;

                    // Update progress bar
                    $('#scan-progress').css('width', progress + '%');
                    $('#scan-progress').text(Math.floor(progress) + '%');

                    // Update detected files
                    if (detectedFiles.length > 0) {
                        let resultHtml = '';
                        detectedFiles.forEach(function(file) {
                            resultHtml += '<li class="list-group-item">' + file + '</li>';
                        });
                        $('#scan-results').html(resultHtml);
                    }

                    // Stop checking progress if the scan is complete
                    if (progress >= 100) {
                        clearInterval(interval);
                        $('#scan-status').text('Scan Complete');
                    }
                });
            }, 500);  // Check progress every 0.5 seconds
        });
    });
});
