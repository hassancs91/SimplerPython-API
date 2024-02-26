// Initialize Ace
var editor = ace.edit("code-editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/python");

// Set font size
editor.setFontSize(28); // Adjust the number to your preferred font size

document.getElementById('run-btn').addEventListener('click', function() {
    const code = editor.getValue(); // Get code from Ace editor
    const outputDiv = document.getElementById('output');

    // Updated API call
    fetch('https://simplerpython-api-ia9fm.kinsta.app/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'code=' + encodeURIComponent(code)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            outputDiv.innerText = data.output;
        } else {
            outputDiv.innerText = 'Error: ' + (data.message || 'Unknown error');
        }
    })
    .catch(error => {
        outputDiv.innerText = 'Error: ' + error;
    });
});
