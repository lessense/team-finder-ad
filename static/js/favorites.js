document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".project-fav-icon").forEach(btn => {
        btn.addEventListener("click", async function(e) {
            e.preventDefault();
            e.stopPropagation();

            const projectId = this.dataset.projectId;
            const csrftoken = document.cookie.split('csrftoken=')[1]?.split(';')[0];

            try {
                const response = await fetch(`/projects/${projectId}/toggle-favorite/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrftoken
                    },
                    body: JSON.stringify({})
                });

                const data = await response.json();

                if (data.favorited) {
                    this.classList.remove("not-favorite");
                    this.classList.add("favorite");
                    this.dataset.fav = "true";
                } else {
                    this.classList.remove("favorite");
                    this.classList.add("not-favorite");
                    this.dataset.fav = "false";
                }
            } catch (error) {
                console.error("Ошибка:", error);
            }
        });
    });
});
