document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "fitnessForm"
            );

        const button =
            document.getElementById(
                "generateButton"
            );


        if (form && button) {

            form.addEventListener(
                "submit",
                () => {

                    button.disabled = true;

                    button.textContent =
                        "Generating your plan...";

                }
            );

        }


        const textareas =
            document.querySelectorAll(
                "textarea"
            );


        textareas.forEach(
            (textarea) => {

                textarea.addEventListener(
                    "input",
                    () => {

                        textarea.style.height =
                            "auto";

                        textarea.style.height =
                            textarea.scrollHeight
                            + "px";

                    }
                );

            }
        );

    }
);