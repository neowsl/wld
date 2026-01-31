// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const shuffle = (array: any[]) => {
    let i = array.length;

    while (i !== 0) {
        const randomIndex = Math.floor(Math.random() * i);
        i--;

        [array[i], array[randomIndex]] = [array[randomIndex], array[i]];
    }

    return array;
};
