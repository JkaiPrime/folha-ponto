<template>
  <div class="container">
    <div class="card-outer">
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
/* Reset */
body {
  font-family: Arial, sans-serif;
  background-color: white;
  margin: 0;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

/* Centralização */
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

/* Layout principal (relógio e card lado a lado) */
.card-outer {
  background: #007bff;
  padding: 40px;
  border-radius: 20px;
  width: 70vw;
  max-width: 5000px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.2);
}


/* Relógio */
.clock-container {
  flex: 1;
  text-align: left;
  padding-right: 20px;
}

.clock {
  font-size: 50px;
  font-weight: bold;
  color: white;
}

/* Card Interno */
.card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  flex: 1;
}

.logo {
  width: 100px;
  margin-bottom: 10px;
}

h1 {
  font-size: 22px;
  margin-bottom: 20px;
}

/* Input */
.input {
  width: calc(100% - 20px);
  padding: 10px;
  font-size: 18px;
  text-align: center;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-bottom: 10px;
  box-sizing: border-box;
}

/* Botão */
.button {
  width: 100%;
  padding: 10px;
  font-size: 18px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: 0.3s;
}

.button:hover {
  background-color: #0056b3;
}

.button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Responsividade */
@media (max-width: 700px) {
  .card-outer {
    flex-direction: column;
    align-items: center;
    width: 90%;
    padding: 20px;
  }

  .clock-container {
    text-align: center;
    padding-right: 0;
    margin-bottom: 20px;
  }

  .clock {
    font-size: 40px;
  }
}
</style>
