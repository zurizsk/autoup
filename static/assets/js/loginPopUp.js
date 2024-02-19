        const popupLoginScreen = document.querySelector(".popupLogin-screen");
        const closeBtn = document.querySelector(".close-btn");
        const openLoginBtn = document.querySelector(".u-btn-2");

       if(openLoginBtn)
       {
         openLoginBtn.addEventListener("click", ()=>{
            popupLoginScreen.classList.add("active") && console.log('Button clicked!');
        });
       }
        closeBtn.addEventListener("click",()=>{
            popupLoginScreen.classList.remove("active")
        });