<template>
  <div class="container">
    <!-- Área que contém relógio e card de registro -->
    <div class="content-wrapper">
      <!-- Relógio grande à esquerda -->
      <div class="clock-container">
        <p class="clock">{{ horaAtual }}</p>
      </div>

      <!-- Card de registro à direita -->
      <div class="card">
        <img src="@/assets/logo.png" alt="Logo" class="logo" />
        <h1>Registro de Ponto</h1>

        <input
          v-model="codigo"
          type="text"
          class="input"
          placeholder="Digite o código (5 dígitos)"
          @input="validarInput"
        />

        <button
          class="button"
          :disabled="codigo.length !== 5"
          @click="enviarCodigo"
        >
          Registrar Ponto
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";

export default {
  setup() {
    const codigo = ref("");
    const horaAtual = ref("");

    const validarInput = () => {
      // Permite somente dígitos e limita a 5 caracteres
      codigo.value = codigo.value.replace(/\D/g, "").slice(0, 5);
    };

    const enviarCodigo = () => {
      alert(`Código ${codigo.value} enviado!`);
      codigo.value = "";
    };

    const atualizarHora = () => {
      const opcoes = { timeZone: "America/Sao_Paulo", hour12: true };
      horaAtual.value = new Date().toLocaleTimeString("pt-BR", opcoes);
    };

    onMounted(() => {
      setInterval(atualizarHora, 1000);
      atualizarHora();
    });

    return {
      codigo,
      horaAtual,
      validarInput,
      enviarCodigo,
    };
  },
};
</script>

<style>
/* Reset + Fonte */
body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  /* Gradiente no corpo inteiro */
  background: linear-gradient(135deg, #004aad, #007bff);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

/* Container principal para centralizar */
.container {
  width: 100%;
  max-width: 1200px;
  display: flex;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

/* Wrapper que agrupa relógio e card dentro de um bloco branco */
.content-wrapper {
  display: flex;
  width: 100%;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  padding: 40px;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
}

/* Relógio */
.clock-container {
  flex: 1;
  text-align: left;
  margin-right: 40px;
}

.clock {
  font-size: 60px;
  font-weight: bold;
  color: #004aad; /* Fica legal puxar pro azul escuro do gradiente */
  margin: 0;
}

/* Card interno (formulário) */
.card {
  flex: 1;
  max-width: 400px;
  text-align: center;
  padding: 20px;
  box-sizing: border-box;
}

.logo {
  width: 100px;
  margin-bottom: 10px;
}

h1 {
  font-size: 22px;
  margin-bottom: 20px;
  color: #004aad;
}

/* Input */
.input {
  width: 100%;
  padding: 12px;
  font-size: 18px;
  text-align: center;
  border: 2px solid #ccc;
  border-radius: 8px;
  margin-bottom: 15px;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.3s;
}

.input:focus {
  border-color: #007bff;
}

/* Botão */
.button {
  width: 100%;
  padding: 12px;
  font-size: 18px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-weight: bold;
}

.button:hover {
  background-color: #005bb5;
}

.button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Responsividade */
@media (max-width: 700px) {
  .content-wrapper {
    flex-direction: column;
    padding: 20px;
  }

  .clock-container {
    text-align: center;
    margin-right: 0;
    margin-bottom: 20px;
  }

  .clock {
    font-size: 40px;
  }
}
</style>
