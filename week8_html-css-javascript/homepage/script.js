document.addEventListener("DOMContentLoaded", function () {
    const projectBlocks = document.querySelectorAll(".project-block-div");
    
    projectBlocks.forEach((block, idx) => {
        setTimeout(() => {
            block.classList.add("animate");
        }, 300 * idx); 
    });

});