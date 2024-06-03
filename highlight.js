
function initNote(){
    //do nothing
}

// Function to highlight text
function highlightText(text) {
    console.log("*highlightText=", text)
    // Create a walker to iterate over all text nodes
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
  
    // Iterate through each text node
    var node;
    while (node = walker.nextNode()) {
        var regex = new RegExp(text, 'gi');
        if (regex.test(node.nodeValue)) {
          console.log("****found")
            // Split text node into parts and wrap the matched part in a span
            var newNode = document.createElement('span');
            newNode.innerHTML = node.nodeValue.replace(regex, '<span style="background-color: lightblue;">$&</span>');
            node.parentNode.replaceChild(newNode, node);
        }
    }
}

window.addEventListener('load', function() {
    // Check if URL contains the highlight parameter
    if (window.location.hash) {
      console.log("***textparam detected=", window.location.hash)
        var textToHighlight = decodeURIComponent(window.location.hash.replace(/\+/g, ' '));
        if (textToHighlight.startsWith("#")) {
          textToHighlight = textToHighlight.substring(1);
        }
        highlightText(textToHighlight);
    }
});

