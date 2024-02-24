// Initialize Ace
var editor = ace.edit("code-editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/python");

// Set font size
editor.setFontSize(28); // Adjust the number to your preferred font size


document.getElementById('run-btn').addEventListener('click', function() {
    const code = editor.getValue(); // Get code from Ace editor
    const outputDiv = document.getElementById('output');

    // Example API call (you'll need to replace this with actual API details)
    fetch('https://api.jdoodle.com/v1/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            script: code,
            language: 'python3',
            versionIndex: '3',
            clientId: 'b29dc52d523ee310225933df80d40669',
            clientSecret: '67ac7b0fccd5167701d7f806f797cf427c3afbe3033273c9edd6dd9f1ff34531'
        }),
    })
    .then(response => response.json())
    .then(data => {
        outputDiv.innerText = data.output;
    })
    .catch(error => {
        outputDiv.innerText = 'Error: ' + error;
    });
});
