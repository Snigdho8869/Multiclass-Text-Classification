function predict() {
    var text = document.getElementById('text').value;
    
    fetch('/suicide-ideation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: text
        })
    })
    .then(function(response) {
        // Convert the response to JSON
        return response.json();
    })
    .then(function(data) {
        var category = data.category;
        document.getElementById('prediction').innerHTML = category[0];
        
        const predictionDiv = document.getElementById('prediction');
        const animation = anime({
            targets: predictionDiv,
            translateY: ["-100%", 0],
            opacity: [0, 1],
            scale: [0.5, 1],
            duration: 1000,
            easing: "spring(1, 80, 10, 0)",
            delay: 500
        });
    })
    .catch(function(error) {
        document.getElementById('prediction').innerHTML = 'Error: ' + error.message;
    });
}
