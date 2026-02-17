const btn = document.getElementById("scrape-btn");

if (btn) {
    btn.addEventListener("click", async () => {
        btn.disabled = true;
        btn.textContent = "Загрузка...";

        try {
            const response = await fetch("/api/scrape", { method: "POST" });
            await response.json();

            if (response.ok) {
                btn.textContent = "Готово! Обновляем...";
                setTimeout(() => location.reload(), 3000);
            } else {
                btn.textContent = "Ошибка";
                setTimeout(() => {
                    btn.textContent = "Обновить новости";
                    btn.disabled = false;
                }, 2000);
            }
        } catch (error) {
            btn.textContent = "Ошибка сети";
            setTimeout(() => {
                btn.textContent = "Обновить новости";
                btn.disabled = false;
            }, 2000);
        }
    });
}
