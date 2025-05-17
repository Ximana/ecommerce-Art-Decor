document.addEventListener('DOMContentLoaded', function() {
        // Controle de quantidade
        const quantityInput = document.getElementById('quantityInput');
        const decreaseBtn = document.getElementById('decreaseQuantity');
        const increaseBtn = document.getElementById('increaseQuantity');
        
        // Estoque máximo disponível
        const estoqueMaximo = {{ produto.estoque }};
    
        decreaseBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
            }
        });
    
        increaseBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            // Limitar ao estoque disponível
            if (currentValue < estoqueMaximo) {
                quantityInput.value = currentValue + 1;
            } else {
                // Mostrar notificação em vez de alerta
                mostrarNotificacao('Quantidade máxima disponível em estoque: ' + estoqueMaximo, 'error');
            }
        });
    
        // Troca de imagem do produto
        const mainProductImage = document.getElementById('mainProductImage');
        const thumbnails = document.querySelectorAll('.product-thumbnail');
    
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // Remove active class from all thumbnails
                thumbnails.forEach(t => t.classList.remove('border', 'border-primary'));
                
                // Add active class to clicked thumbnail
                this.classList.add('border', 'border-primary');
                
                // Change main image
                mainProductImage.src = this.src;
                mainProductImage.alt = this.alt;
            });
        });
        
        // Adicionar ao carrinho com AJAX
        const addToCartForm = document.getElementById('addToCartForm');
        if (addToCartForm) {
            addToCartForm.addEventListener('submit', function(event) {
                // Impedir o envio tradicional do formulário
                event.preventDefault();
                
                const formData = new FormData(this);
                const addToCartBtn = document.getElementById('addToCartBtn');
                const originalText = addToCartBtn.innerHTML;
                
                // Desativar o botão durante o processamento
                addToCartBtn.disabled = true;
                addToCartBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Processando...';
                
                // Enviar via AJAX
                fetch('{% url "carrinhos:adicionar" %}', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro na resposta do servidor');
                    }
                    return response.json();
                })
                .then(data => {
                    // Feedback visual            
                    if (data.status === 'success') {
                        // Atualizar contador do carrinho se existir
                        const cartCounter = document.getElementById('cartCounter');
                        if (cartCounter) {
                            cartCounter.textContent = data.quantidade_total;
                            cartCounter.classList.remove('d-none');
                        }
                        
                        // Alterar botão para mostrar sucesso
                        addToCartBtn.innerHTML = '<i class="fas fa-check me-2"></i> Adicionado!';
                        addToCartBtn.classList.replace('btn-primary', 'btn-success');
                        
                        // Mensagem de sucesso usando APENAS a função personalizada
                        mostrarNotificacao(data.message || 'Produto adicionado ao carrinho com sucesso!', 'success');
                        
                        // Resetar o campo de quantidade para 1
                        document.getElementById('quantityInput').value = '1';
                    } else {
                        // Mensagem de erro
                        mostrarNotificacao(data.message || 'Erro ao adicionar ao carrinho', 'error');
                    }
                    
                    // Restaurar botão após 2 segundos em caso de sucesso
                    if (data.status === 'success') {
                        setTimeout(() => {
                            addToCartBtn.innerHTML = originalText;
                            addToCartBtn.classList.replace('btn-success', 'btn-primary');
                            addToCartBtn.disabled = false;
                        }, 2000);
                    } else {
                        // Restaurar botão imediatamente em caso de erro
                        addToCartBtn.innerHTML = originalText;
                        addToCartBtn.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    mostrarNotificacao('Erro ao processar sua solicitação. Tente novamente.', 'error');
                    
                    // Restaurar botão em caso de erro
                    addToCartBtn.innerHTML = originalText;
                    addToCartBtn.disabled = false;
                });
            });
        }
        
        // Adicionar aos favoritos
        const addToFavoritesBtn = document.getElementById('addToFavoritesBtn');
        if (addToFavoritesBtn) {
            addToFavoritesBtn.addEventListener('click', function() {
                // Verificar se o usuário está autenticado
                {% if not user.is_authenticated %}
                    mostrarNotificacao('Você precisa estar logado para adicionar produtos aos favoritos', 'error');
                    return;
                {% endif %}
                
                const produtoId = this.getAttribute('data-produto-id');
                const heartIcon = this.querySelector('i');
                
                // Cria os dados para o POST
                const formData = new FormData();
                formData.append('produto_id', produtoId);
                formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');
                
                // Envia a requisição AJAX
                fetch('{% url "usuarios:adicionar_desejo" %}', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Alterna a classe do botão para indicar o estado
                        if (data.added) {
                            heartIcon.classList.add('fas');
                            heartIcon.classList.remove('far');
                        } else {
                            heartIcon.classList.add('far');
                            heartIcon.classList.remove('fas');
                        }
                        
                        // Exibe notificação de sucesso
                        mostrarNotificacao(data.message, 'success');
                    } else {
                        mostrarNotificacao(data.message || 'Erro ao processar sua solicitação', 'error');
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    mostrarNotificacao('Erro ao processar sua solicitação', 'error');
                });
            });
        }

        // Avaliações
        const reviewForm = document.getElementById('reviewForm');
        if (reviewForm) {
            reviewForm.addEventListener('submit', function(event) {
                event.preventDefault();
                
                const formData = new FormData(this);
                const submitBtn = document.getElementById('submitReviewBtn');
                const originalText = submitBtn.innerHTML;
                
                // Verificar se uma nota foi selecionada
                if (!formData.get('nota')) {
                    mostrarNotificacao('Por favor, selecione uma nota para o produto.', 'error');
                    return;
                }
                
                // Desativar o botão durante o processamento
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Processando...';
                
                // Enviar via AJAX
                fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        mostrarNotificacao(data.message, 'success');
                        // Recarregar a página para mostrar a avaliação atualizada
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        mostrarNotificacao(data.message || 'Erro ao enviar avaliação', 'error');
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    mostrarNotificacao('Erro ao processar sua solicitação. Tente novamente.', 'error');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                });
            });
        }

        // Remover avaliação
        const deleteReviewBtns = document.querySelectorAll('.delete-review-btn');
        deleteReviewBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                if (confirm('Tem certeza que deseja remover sua avaliação?')) {
                    const avaliacaoId = this.getAttribute('data-avaliacao-id');
                    
                    fetch(`/produtos/remover-avaliacao/${avaliacaoId}/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': '{{ csrf_token }}'
                        },
                        credentials: 'same-origin'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            mostrarNotificacao(data.message, 'success');
                            // Recarregar a página para atualizar as avaliações
                            setTimeout(() => {
                                window.location.reload();
                            }, 1500);
                        } else {
                            mostrarNotificacao(data.message || 'Erro ao remover avaliação', 'error');
                        }
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                        mostrarNotificacao('Erro ao processar sua solicitação. Tente novamente.', 'error');
                    });
                }
            });
        });
    });
    
    // Função para mostrar notificações (mantida separada para reutilização)
    function mostrarNotificacao(mensagem, tipo) {
        // Remover notificações existentes para evitar empilhamento
        const notificacoesExistentes = document.querySelectorAll('.notification');
        notificacoesExistentes.forEach(notif => {
            notif.classList.remove('show');
            setTimeout(() => {
                if (notif.parentNode) {
                    notif.parentNode.removeChild(notif);
                }
            }, 300);
        });
        
        // Criar elemento de notificação
        const notificacao = document.createElement('div');
        notificacao.className = `notification ${tipo}`;
        notificacao.innerHTML = `
            <div class="notification-content">
                <i class="fas ${tipo === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
                <span>${mensagem}</span>
            </div>
        `;
        
        // Adicionar ao DOM
        document.body.appendChild(notificacao);
        
        // Mostrar com animação
        setTimeout(() => {
            notificacao.classList.add('show');
        }, 10);
        
        // Remover após alguns segundos
        setTimeout(() => {
            notificacao.classList.remove('show');
            setTimeout(() => {
                if (notificacao.parentNode) {
                    document.body.removeChild(notificacao);
                }
            }, 300);
        }, 5000); // Aumentei para 5 segundos para dar mais tempo de leitura
    }