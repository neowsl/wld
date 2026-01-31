<script lang="ts">
    import { BookMarked, QrCode } from "@lucide/svelte";
    import { resolve } from "$app/paths";
    import qrcode from "$lib/assets/qr-code.png";
    import data from "$lib/dictionary.json";
    import { shuffle } from "$lib/utils";

    const ROW_HEIGHT = 36.6;
    const SCROLL_STEP = 3;
    const FRICTION = 0.95;
    const VELOCITY_MULTIPLIER = 2;

    let windowHeight: number;

    $: viewportSize = Math.floor((windowHeight - 80) / ROW_HEIGHT);

    const shuffledData: string[] = shuffle(Object.keys(data));

    let startIndex = 0;
    let isDragging = false;
    let selectedWord = "";

    $: visibleRows = shuffledData.slice(startIndex, startIndex + viewportSize);
    $: scrollFraction = startIndex / (shuffledData.length - viewportSize);

    let lastTouchY = 0;
    let velocity = 0;
    let lastTouchTime = 0;
    let animationFrame = 0;

    const handleWheel = (e: WheelEvent) => {
        const direction = Math.sign(e.deltaY);
        updateIndex(startIndex + direction * SCROLL_STEP);
    };

    const handleMouseDown = () => {
        isDragging = true;
        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("mouseup", handleMouseUp);
    };

    const handleMouseMove = (e: MouseEvent) => {
        if (!isDragging) return;

        const rect = document
            .getElementById("scroll-track")!
            .getBoundingClientRect();
        const offsetY = e.clientY - rect.top;
        const fraction = Math.max(0, Math.min(1, offsetY / rect.height));

        updateIndex(
            Math.floor(fraction * (shuffledData.length - viewportSize)),
        );
    };

    const handleMouseUp = () => {
        isDragging = false;
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("mouseup", handleMouseUp);
    };

    const stopInertia = () => {
        cancelAnimationFrame(animationFrame);
        velocity = 0;
    };

    const startInertia = () => {
        if (Math.abs(velocity) < 0.1) return;

        velocity *= FRICTION;
        updateIndex(startIndex + velocity);

        animationFrame = requestAnimationFrame(startInertia);
    };

    const handleTouchStart = (e: TouchEvent) => {
        stopInertia();
        lastTouchY = e.touches[0].clientY;
        lastTouchTime = performance.now();
    };

    const handleTouchMove = (e: TouchEvent) => {
        const currentY = e.touches[0].clientY;
        const currentTime = performance.now();

        const deltaY = lastTouchY - currentY;
        const deltaTime = currentTime - lastTouchTime;

        if (deltaTime > 0) {
            velocity = (deltaY / ROW_HEIGHT / deltaTime) * 16;
        }

        const rowsToScroll = deltaY / ROW_HEIGHT;
        updateIndex(startIndex + rowsToScroll);

        lastTouchY = currentY;
        lastTouchTime = currentTime;
    };

    const handleTouchEnd = () => {
        velocity *= VELOCITY_MULTIPLIER;
        startInertia();
    };

    const updateIndex = (x: number) => {
        x = Math.round(x);
        startIndex = Math.max(
            0,
            Math.min(shuffledData.length - viewportSize, x),
        );
    };

    const showDefinition = (word: string) => () => {
        selectedWord = word;
        document.getElementById("definition")!.showModal();
    };
</script>

<svelte:window bind:innerHeight={windowHeight} />

<nav class="flex h-20 items-center px-8">
    <a class="text-xl font-bold link-hover md:text-3xl" href={resolve("/")}>
        Whitaker's Latin Dictionary
    </a>
    <div class="grow"></div>
    <button
        class="btn btn-square btn-ghost"
        on:click={() => document.getElementById("link")!.showModal()}
    >
        <QrCode />
    </button>
</nav>

<div
    class="h-full border-t border-base-content/10 text-xl select-none"
    on:wheel|preventDefault={handleWheel}
    on:touchstart={handleTouchStart}
    on:touchmove|preventDefault={handleTouchMove}
    on:touchend={handleTouchEnd}
    aria-hidden="true"
>
    <div class="flex">
        <div class="grow px-8">
            <ul class="list w-full divide-y divide-base-content/10 font-mono">
                {#each visibleRows as word, i (i)}
                    <li
                        class="py-2 transition-colors hover:bg-base-200"
                        on:click={showDefinition(word)}
                    >
                        <span class="text-base-content/30">
                            {(startIndex + i).toString().padStart(5, "0")}
                        </span>
                        &nbsp;
                        <span class="font-bold">{word.split(",")[0]}</span>
                    </li>
                {/each}
            </ul>
        </div>

        <div
            id="scroll-track"
            class="relative w-4 cursor-pointer border-l border-base-content/10 bg-base-200"
            on:mousedown={handleMouseDown}
            aria-hidden="true"
        >
            <div
                class="absolute w-full bg-primary"
                style="height: 40px; top: calc({scrollFraction} * (100% - 40px)); transition: {isDragging
                    ? 'none'
                    : 'top 0.1s'}"
            ></div>
        </div>
    </div>
</div>

<dialog id="definition" class="modal">
    <div class="modal-box">
        <h3 class="flex items-center gap-4 text-lg font-bold">
            <BookMarked />{selectedWord}
        </h3>
        <p class="py-4">{data[selectedWord]}</p>
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>

<dialog id="link" class="modal">
    <div class="modal-box">
        <h3 class="text-2xl font-bold">https://neowsl.github.io/wld</h3>
        <p class="py-4">
            <img src={qrcode} alt="QR code" />
        </p>
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>
