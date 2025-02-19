<template>
  <div class="container">

    <div class="content-wrapper">
      <!-- Relógio grande à esquerda -->
      <div class="clock-container">
        <p class="clock">{{ horaAtual }}</p>
      </div>

      <div class="card">
        <img src="@/assets/logo.svg" srcset="@/assets/logo.svg" alt="Logo" class="logo" />
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
      //Após a conclusão do back, colocar a req para a api do back
      alert(`Código ${codigo.value} enviado!`);
      codigo.value = "";
    };

    const atualizarHora = () => {
      const opcoes = { timeZone: "America/Sao_Paulo", hour12: false };
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


.container {
  width: 100%;
  max-width: 1200px;
  display: flex;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}


.content-wrapper {
  display: flex;
  width: 100%;
  background:rgb(255, 255, 255);
  border-radius: 20px;
  padding: 40px;
  justify-content: space-between;
  align-items: center;
  box-sizing: border-box;
  /*box-shadow: 0 0 10px 2px black;*/ 
  border: 3px solid black;
}

.clock-container {
  flex: 1;
  text-align: left;
  margin-right: 40px;
}

.clock {
  font-size: 60px;
  font-weight: bold;
  color:rgb(0, 5, 10);
  margin: 0;
}


.card {
  flex: 1;
  max-width: 400px;
  text-align: center;
  padding: 20px;
  box-sizing: border-box;
  background: #fff;  
  border-radius: 10px;
  box-shadow: 0 0 10px 2px black; 
}

.logo {
  width: 100px;
  margin-bottom: 10px;
}

h1 {
  font-size: 22px;
  margin-bottom: 20px;
  color:rgb(0, 0, 0);
}


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
