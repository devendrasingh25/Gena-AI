#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;

    for (int i = 0; i < 2 * n; i++) {
        int star, space;

        if (i < n) {
            star = n - i;
            space = 2 * i;
        } else {
            star = i - n + 1;
            space = 2 * (2 * n - i - 1);
        }

        for (int j = 0; j < space / 2; j++)
            cout << " ";

        for (int j = 0; j < star; j++)
            cout << "* ";

        cout << endl;
    }

    return 0;
}