<template>
  <div id="reportCover" class="page-break-after">
    <div class="header-section">
      <div class="text-h3 text-bold q-mb-sm" v-text="props.title" />
      <div class="text-h4 text-bold q-mb-sm" v-text="props.nameSubtitle" />
      <div class="text-h5" v-text="props.idSubtitle" />
      <div class="date" v-text="currDate" />
    </div>
    <slot />

    <div class="footer-section">
      <div class="logos">
        <img
          class="bc-water-tool logo"
          src="/bclogo.png"
          :alt="`bc logo`"
        />
        <span>Powered by:</span>
        <img
          class="fs logo"
          src="/foundry-spatial-logo-with-text.svg"
          :alt="`Foundry Spatial logo`"
        />
      </div>
      <div class="logos">
        <a target="_blank" href="https://creativecommons.org/licenses/by/3.0/">
          License: CC BY 3.0
        </a>
      </div>
      <div class="url has-text-grey-light" v-text="url" />
    </div>
  </div>
</template>

<script setup>
import dayjs from "dayjs";
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  nameSubtitle: {
    type: String,
    required: false,
    default: null,
  },
  idSubtitle: {
    type: String,
    required: false,
    default: null,
  }
});

const currDate = computed(() => {
  return dayjs().format("MMMM D, YYYY");
});

const url = computed(() => {
  // get module path from route
  const modulePath = route.path.split("/static-report")[0];
  return `watertool.ca/${modulePath}` || "";
});
</script>

<style lang="scss">
#reportCover {
  height: calc(11in - (2 * 48px)); // 11inch - (2 * 48px margin)
  display: flex;
  flex-direction: column;
  align-items: stretch;

  .header-section {
    background-color: #eeeeee;
    padding: 1rem;

    div {
      color: $primary-font-color;
    }

    .date {
      margin-top: 1.25rem;
    }
  }

  .footer-section {
    font-size: 0.625rem;

    .logos {
      display: flex;
      justify-content: center;
      align-items: center;
      margin-bottom: 4px;

      .logo {
        &.bc-water-tool {
          margin: 0 0.5rem;
          height: 4rem;
        }

        &.fs {
          margin: 0 0.25rem;
          height: 3rem;
        }
      }
    }

    .url {
      text-align: center;
    }
  }
}
</style>
