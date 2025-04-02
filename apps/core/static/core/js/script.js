
// Javascript para a contador do carrinho

document.addEventListener('DOMContentLoaded', function() {
    // Selecionar todos os formulários de adição ao carrinho
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Enviar formulário via AJAX
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Atualizar contador do carrinho
                    const cartCounters = document.querySelectorAll('.cart-count');
                    cartCounters.forEach(counter => {
                        counter.textContent = data.quantidade_total;
                    });
                    
                    // Opcional: exibir uma mensagem de sucesso
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Erro ao adicionar ao carrinho:', error);
            });
        });
    });
});